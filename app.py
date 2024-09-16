from flask import Flask, jsonify, request, session, redirect, url_for
import smtplib
from email.mime.text import MIMEText
import datetime
import time
from threading import Thread
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)

# Simulate a database of users (use SQLAlchemy for real-world use)
users = {'admin': {'password': 'adminpass'}}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Define User Loader (required by Flask-Login)
@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

# Simulated storage for scheduled patches (could be a DB)
scheduled_patches = []

# Email sending function
def send_email(subject, recipient, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'youremail@example.com'  # Replace with your email
    msg['To'] = recipient

    # Replace with your SMTP server details
    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_user = 'youremail@example.com'  # Replace with your email
    smtp_password = 'yourpassword'  # Replace with your email password

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Encrypt the connection
            server.login(smtp_user, smtp_password)
            server.sendmail(smtp_user, recipient, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

# Route to handle scan and send email
@app.route('/send-email', methods=['GET'])
@login_required
def scan_and_send_email():
    # Send an email when this route is accessed
    send_email(
        subject="VulnGuard Scan Initiated",
        recipient="client@example.com",  # Replace with the recipient's email
        body="Your scan is in progress. You will receive a report shortly."
    )
    return jsonify({"message": "Email sent successfully!"})

# Route to schedule patch management
@app.route('/schedule-patch', methods=['POST'])
@login_required
def schedule_patch():
    data = request.get_json()
    patch_time = data.get('patch_time')
    patch_time = datetime.datetime.strptime(patch_time, '%Y-%m-%d %H:%M:%S')

    # Store patch schedule
    scheduled_patches.append({
        'client': data.get('client'),
        'email': data.get('email'),
        'patch_time': patch_time
    })

    return jsonify({"message": "Patch scheduled successfully!"})

# Function to check and apply scheduled patches
def apply_patches():
    while True:
        current_time = datetime.datetime.now()
        for patch in scheduled_patches:
            if patch['patch_time'] <= current_time:
                # Simulate patch application
                print(f"Applying patch for {patch['client']}")

                # Send an email after patch is applied
                send_email(
                    subject="Patch Applied Successfully",
                    recipient=patch['email'],
                    body=f"Dear {patch['client']},\n\nYour patch has been applied successfully at {current_time}.\n\nBest regards,\nVulnGuard Team"
                )

                # Remove the patch from the schedule once applied
                scheduled_patches.remove(patch)

        time.sleep(60)  # Check every minute

# User login route
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username in users and users[username]['password'] == password:
        user = User(username)
        login_user(user)
        return jsonify({"message": "Login successful!"})
    return jsonify({"message": "Invalid credentials!"}), 401

# User logout route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Protect a route (e.g., dashboard)
@app.route('/dashboard')
@login_required
def dashboard():
    return jsonify({"message": f"Welcome to your dashboard, {current_user.id}!"})

if __name__ == '__main__':
    # Start the patch management process in the background
    patch_thread = Thread(target=apply_patches)
    patch_thread.daemon = True
    patch_thread.start()

    app.run(host='0.0.0.0', port=5000)