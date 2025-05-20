# Import and patch eventlet first, before any other imports
import eventlet
eventlet.monkey_patch()

# Now import other modules
import sys
import logging
import time
try:
    from flask import Flask, render_template, request, redirect, url_for, session
    from flask_socketio import SocketIO, join_room, emit
    import uuid
    from datetime import datetime, timedelta
    from werkzeug.security import generate_password_hash, check_password_hash
    import socket
except ImportError as e:
    print(f"Dependency error: {e}")
    print("Please install required packages: pip install flask flask-socketio flask-session werkzeug eventlet")
    sys.exit(1)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = "secret123"
app.config['SESSION_TYPE'] = 'filesystem'

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Store rooms and admin credentials
rooms = {}  # {room_id: {key, expiry, users, messages, theme}}
admin_credentials = {
    'admin': generate_password_hash('admin123')  # Default admin:admin123
}

# Routes
@app.route('/')
def index():
    logger.debug("Serving index page")
    return render_template('index.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        logger.debug(f"Admin login attempt: {username}")
        if username in admin_credentials and check_password_hash(admin_credentials[username], password):
            session['admin'] = username
            logger.info(f"Admin {username} logged in successfully")
            return redirect(url_for('admin_dashboard'))
        logger.warning(f"Failed login attempt for {username}")
        return render_template('admin.html', error='Invalid credentials')
    return render_template('admin.html')

@app.route('/admin/dashboard', methods=['GET', 'POST'])
def admin_dashboard():
    if 'admin' not in session:
        logger.warning("Unauthorized access to admin dashboard")
        return redirect(url_for('admin_login'))
    if request.method == 'POST':
        key = str(uuid.uuid4())[:8]
        duration = int(request.form.get('duration'))
        theme = request.form.get('theme', '#eee')
        room_id = str(uuid.uuid4())
        expiry = datetime.now() + timedelta(minutes=duration)
        rooms[room_id] = {
            'key': key,
            'expiry': expiry,
            'users': {},
            'messages': [],
            'theme': theme
        }
        room_url = f"{request.url_root}?room={room_id}"
        logger.info(f"Created room {room_id} with key {key}, expires at {expiry}")
        return render_template('admin_dashboard.html', room_url=room_url, key=key, rooms=rooms)
    return render_template('admin_dashboard.html', rooms=rooms)

# SocketIO Events
@socketio.on('connect', namespace='/')
def handle_connect():
    logger.info(f"Client connected from {request.remote_addr}")

@socketio.on('connect_error', namespace='/')
def handle_connect_error(error):
    logger.error(f"Client connection failed: {error}")

@socketio.on('disconnect', namespace='/')
def handle_disconnect():
    logger.info(f"Client disconnected")

@socketio.on('join_room', namespace='/')
def handle_join_room(data):
    room_id = data.get('roomId')
    username = data.get('username')
    key = data.get('key')

    if not room_id or room_id not in rooms:
        emit('access_denied', 'Room does not exist or has expired')
        return
    if key != rooms[room_id]['key']:
        emit('access_denied', 'Invalid room key')
        return

    join_room(room_id)
    rooms[room_id]['users'][username] = username
    emit('access_granted', {
        'key': rooms[room_id]['key'],
        'theme': rooms[room_id]['theme'],
        'messages': rooms[room_id]['messages']
    })
    emit('user_list', list(rooms[room_id]['users'].values()), room=room_id)
    system_msg = {
        'username': 'System',
        'message': f"{username} has joined the chat",
        'type': 'system',
        'timestamp': datetime.now().isoformat()
    }
    rooms[room_id]['messages'].append(system_msg)
    emit('message', system_msg, room=room_id)

@socketio.on('message', namespace='/')
def handle_message(data):
    room_id = data.get('roomId')
    if room_id not in rooms:
        emit('room_expired')
        return
    msg_data = {
        'username': data['username'],
        'message': data['message'],
        'type': 'user',
        'timestamp': datetime.now().isoformat()
    }
    rooms[room_id]['messages'].append(msg_data)
    emit('message', msg_data, room=room_id)

@socketio.on('user_left', namespace='/')
def handle_user_left(username):
    for room_id, room in rooms.items():
        if username in room['users']:
            del room['users'][username]
            emit('user_list', list(room['users'].values()), room=room_id)
            msg = {
                'username': 'System',
                'message': f"{username} has left the chat",
                'type': 'system',
                'timestamp': datetime.now().isoformat()
            }
            room['messages'].append(msg)
            emit('message', msg, room=room_id)


# Background task to check room expiry
def check_room_expiry():
    try:
        while True:
            current_time = datetime.now()
            expired_rooms = [room_id for room_id, room in rooms.items() if room['expiry'] < current_time]
            for room_id in expired_rooms:
                logger.info(f"Expiring room {room_id}")
                socketio.emit('room_expired', room=room_id)
                del rooms[room_id]
            eventlet.sleep(60)
    except Exception as e:
        logger.error(f"Error in check_room_expiry: {e}")

# Function to find an available port
def find_available_port(start_port):
    port = start_port
    max_attempts = 10
    attempt = 0
    while attempt < max_attempts:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.bind(('127.0.0.1', port))
            sock.close()
            logger.info(f"Port {port} is available")
            return port
        except OSError as e:
            logger.warning(f"Port {port} is in use: {e}")
            port += 1
            attempt += 1
            time.sleep(1)  # Wait briefly to allow port release
    logger.error(f"Could not find an available port after {max_attempts} attempts")
    sys.exit(1)

# Main execution
if __name__ == "__main__":
    try:
        port = find_available_port(5000)
        logger.info(f"Starting Flask-SocketIO server on port {port}")
        socketio.start_background_task(check_room_expiry)
        socketio.run(app, host="127.0.0.1", port=port, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)