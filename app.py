from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.text import MIMEText
import datetime
from threading import Thread
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import bcrypt

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# SQLAlchemy setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vulnguard.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

# User model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Patch model
class Patch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    client_email = db.Column(db.String(120), nullable=False)
    patch_time = db.Column(db.DateTime, nullable=False)
    applied = db.Column(db.Boolean, default=False)

# Create tables in the database
with app.app_context():
    db.create_all()

# Email sending function
def send_email(subject, recipient, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'youremail@example.com'
    msg['To'] = recipient

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'youremail@example.com'
    smtp_password = 'yourpassword'

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipient, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# User registration route with password hashing and validation
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if len(username) < 3 or len(password) < 6:
        return jsonify({"message": "Username must be at least 3 characters and password at least 6 characters!"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User already exists!"}), 400

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(username=username, password=hashed_password)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User registered successfully!"})

# User login route with password verification
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
        login_user(user)
        return jsonify({"message": "Login successful!"})
    return jsonify({"message": "Invalid credentials!"}), 401

# User logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return jsonify({"message": "You have been logged out!"}), 200

# Route to schedule patch management
@app.route('/schedule-patch', methods=['POST'])
@login_required
def schedule_patch():
    data = request.get_json()
    patch_time = datetime.datetime.strptime(data.get('patch_time'), '%Y-%m-%d %H:%M:%S')
    
    new_patch = Patch(
        client_name=current_user.username,
        client_email="client@example.com",  # You can make this dynamic
        patch_time=patch_time
    )
    db.session.add(new_patch)
    db.session.commit()

    return jsonify({"message": "Patch scheduled successfully!"})

# Function to check and apply scheduled patches
def apply_patches():
    while True:
        current_time = datetime.datetime.now()
        patches = Patch.query.filter(Patch.patch_time <= current_time, Patch.applied == False).all()

        for patch in patches:
            send_email(
                subject="Patch Applied Successfully",
                recipient=patch.client_email,
                body=f"Dear {patch.client_name}, your patch has been applied successfully at {current_time}."
            )
            patch.applied = True
            db.session.commit()

        time.sleep(60)

# User dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    patches = Patch.query.filter_by(client_name=current_user.username).all()
    return render_template('dashboard.html', patches=patches)

if __name__ == '__main__':
    patch_thread = Thread(target=apply_patches)
    patch_thread.daemon = True
    patch_thread.start()

    app.run(host='0.0.0.0', port=5000)