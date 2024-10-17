from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a random secret key
socketio = SocketIO(app)

# In-memory storage for users
users = {}

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username in users and users[username] == password:
            session['username'] = username
            return redirect(url_for('chat', room_code=username))
        return 'Invalid credentials', 401
    return render_template('login.html')

@app.route('/chat/<room_code>', methods=['GET', 'POST'])
def chat(room_code):
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('room.html', room_code=room_code)

@socketio.on('message')
def handle_message(data):
    emit('message', data, broadcast=True)

@socketio.on('join')
def on_join(data):
    room = data['room']
    username = session['username']
    emit('message', {'msg': f'{username} has joined the room.'}, room=room)

if __name__ == '__main__':
    socketio.run(app, debug=True)
