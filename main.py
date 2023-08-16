from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat_app'
db = SQLAlchemy(app)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)


# Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender = db.Column(db.String(50), nullable=False)
    recipient = db.Column(db.String(50), nullable=False)
    message = db.Column(db.String(500), nullable=False)


# ... (other routes)

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))


# Dummy user data for demonstration purposes
users = {
    "user1": "password1",
    "user2": "password2",
    # Add more users...
}

messages = {}  # Use a dictionary to store messages


# Manual user authentication
def authenticate(username, password):
    if username in users and users[username] == password:
        return True
    return False


@app.route("/")
def index():
    if "username" in session:
        return redirect(url_for("chat"))
    registered_users = users.keys()  # Get registered usernames
    return render_template("login.html", registered_users=registered_users)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Perform registration logic here (e.g., add user to the users dictionary)
        users[username] = password

        return redirect(url_for("index"))

    return render_template("registration.html")


@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    if authenticate(username, password):
        session["username"] = username
        return redirect(url_for("chat"))
    else:
        return redirect(url_for("index"))


@app.route("/chat")
def chat():
    if "username" in session:
        return render_template("chat.html", username=session["username"], messages=messages)
    return redirect(url_for("index"))


# ... (previous code)

@app.route("/chat/<recipient>", methods=["GET", "POST"])
def chat_with(recipient):
    if "username" in session:
        if request.method == "POST":
            message_text = request.form["message"]
            sender = session["username"]

            new_message = Message(sender=sender, recipient=recipient, message=message_text)
            db.session.add(new_message)
            db.session.commit()

        selected_user = recipient

        messages = Message.query.filter(
            (Message.sender == session["username"] and Message.recipient == selected_user) or (
                    Message.sender == selected_user and Message.recipient == session["username"])).all()

        return render_template("chat.html", username=session["username"], messages=messages,
                               selected_user=selected_user, registered_users=User.query.all())
    return redirect(url_for("index"))


@app.route("/send_message", methods=["POST"])
def send_message():
    if "username" in session:
        message = request.form["message"]
        sender = session["username"]
        messages.append({"sender": sender, "message": message})
        return redirect(url_for("chat"))
    return redirect(url_for("index"))



if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)