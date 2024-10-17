from flask import Flask, render_template, redirect, url_for, request, session
from flask_socketio import SocketIO, emit
import random
import string

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

rooms = {}  # Dictionary to hold room information

def generate_unique_code(length):
    """Generate a unique room code."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@app.route("/", methods=["POST", "GET"])
def home():
    session.clear()  # Clear session for fresh login
    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")

        if not name or not password:
            return render_template("home.html", error="Please enter a name and password.")

        if password != name:  # Check if password matches the name
            return render_template("home.html", error="Password must match your name.")

        room = generate_unique_code(4)
        rooms[room] = {"members": 0, "messages": []}

        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))
    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@socketio.on("message")
def handle_message(data):
    room = session.get("room")
    if room in rooms:
        msg = {
            "name": session.get("name"),
            "message": data['data']
        }
        rooms[room]["messages"].append(msg)
        emit("message", msg, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, debug=True)
