# Secure Chat Room

## Overview

Secure Chat Room is a web-based chat application built with Flask and SocketIO. It allows users to create temporary chat rooms with unique keys, join rooms, and chat in real-time. The app includes an admin dashboard for creating rooms and managing active rooms. Rooms have a set duration, after which they expire automatically.

## Features

- **Admin Dashboard**: Create chat rooms with a unique key and set duration.
- **Real-Time Chat**: Users can join rooms and chat in real-time using SocketIO.
- **Room Expiry**: Rooms automatically expire after the set duration.
- **User Management**: Displays a list of online users in the room.
- **Secure Access**: Rooms are protected with a unique key.

## Tech Stack

- **Backend**: Flask, Flask-SocketIO, Eventlet
- **Frontend**: HTML, Bootstrap 5, jQuery, Socket.IO client
- **Python Version**: 3.8 or higher

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- A web browser (e.g., Chrome, Firefox)

## Setup Instructions

### 1. Clone the Repository

If your project is hosted on a Git repository, clone it. Otherwise, copy the project files to your local machine.

```bash
git clone <repository-url>
cd secure-chat-room
```

### 2. Install Dependencies

Install the required Python packages listed in `requirements.txt`.

```bash
pip install -r requirements.txt
```

### 3. Project Structure

Ensure your project directory looks like this:

```
secure-chat-room/
│
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── README.md           # Project documentation
│
└── templates/
    ├── index.html      # Chat room interface
    ├── admin.html      # Admin login page
    └── admin_dashboard.html  # Admin dashboard for creating rooms
```

### 4. Run the Application

Start the Flask server:

```bash
python app.py
```

The server will start on `http://127.0.0.1:5000`.

### 5. Access the Application

- **Admin Dashboard**:
  - Open `http://localhost:5000/admin` in your browser.
  - Log in with the default credentials: `admin` / `admin123`.
  - Create a new room by specifying a duration (in minutes) and a theme color.
  - Note the generated room URL and key.
- **Join a Room**:
  - Open the room URL (e.g., `http://localhost:5000/?room=<room_id>`).
  - Enter a username and the room key, then click "Join Room".
  - Start chatting with other users in the room.

## Usage Notes

- Rooms expire automatically after the set duration.
- If a room expires, users will be redirected to the home page.
- The app uses HTTP polling for SocketIO communication to ensure compatibility in environments where WebSocket is blocked.

## Troubleshooting

- **Connection Issues**:
  - If you see "Failed to connect to server" in the browser, ensure the server is running and there are no firewall/antivirus restrictions.
  - Check the browser console (F12 &gt; Console) and server logs for errors.
- **Port Conflicts**:
  - The app automatically finds an available port starting from 5000. If it fails, ensure no other process is using the port.
- **Dependencies**:
  - Ensure all dependencies are installed correctly. Run `pip install -r requirements.txt` again if you encounter issues.

## Future Improvements

- Add message persistence using a database.
- Implement user typing indicators.
- Add support for private messages between users.
- Enhance security with user authentication for the admin dashboard.

## License

© 2025 Dhruv Gahlot. All Rights Reserved.