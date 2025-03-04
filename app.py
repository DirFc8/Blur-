import os
import sqlite3
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'fallback-secret-key')
socketio = SocketIO(app, async_mode='threading')  # Use threading mode for compatibility with Gunicorn

DATABASE = 'chat.db'

def init_db():
    if not os.path.exists(DATABASE):
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''
            CREATE TABLE messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()

init_db()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form.get('username')
        if username and username.strip():
            session['username'] = username.strip()
            return redirect(url_for('chat'))
    return render_template('index.html')

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('chat.html', username=session['username'])

@app.route('/messages')
def messages():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT username, message, timestamp FROM messages ORDER BY id DESC LIMIT 50")
    rows = c.fetchall()
    conn.close()
    msgs = []
    for row in reversed(rows):
        msgs.append({
            'username': row[0],
            'message': row[1],
            'timestamp': row[2]
        })
    return jsonify(msgs)

@socketio.on('chat_message')
def handle_chat_message(data):
    username = data.get('username')
    message = data.get('message')
    if username and message:
        # Save message to the database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute("INSERT INTO messages (username, message) VALUES (?, ?)", (username, message))
        conn.commit()
        conn.close()
        # Broadcast the message to all connected clients
        emit('chat_message', {'username': username, 'message': message}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
