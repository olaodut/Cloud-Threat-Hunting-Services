from flask import Flask, jsonify, request, session, redirect, url_for
import smtplib
from email.mime.text import MIMEText
import datetime
import time
from threading import Thread
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import stripe  # For payment integration

app = Flask(__name__)
app.secret_key = 'your_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

# Stripe configuration
stripe.api_key = 'your_stripe_secret_key'

# Simulate a database of users (for simplicity)
users = {
    'admin': {'password': 'adminpass', 'role': 'admin'},
    'user': {'password': 'userpass', 'role': 'user'}
}

# Simulated storage for scheduled patches
scheduled_patches = []

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None

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

# Scan history and patch history routes
@app.route('/scan-history')
@login_required
def scan_history():
    scans = [{"date": "2024-09-16", "status": "Completed"}, {"date": "2024-09-10", "status": "Completed"}]
    return jsonify(scans)

@app.route('/patch-history')
@login_required
def patch_history():
    patches = [{"date": "2024-09-15", "status": "Applied"}, {"date": "2024-09-01", "status": "Failed"}]
    return jsonify(patches)

# Route for sending scan report emails
@app.route('/send-scan-report', methods=['POST'])
@login_required
def send_scan_report():
    data = request.get_json()
    email = data.get('email')
    send_email("Your Vulnerability Scan Report", email, "Scan completed successfully.")
    return jsonify({"message": "Report sent successfully!"})

# Security suggestions
@app.route('/security-suggestions', methods=['GET'])
@login_required
def security_suggestions():
    suggestions = ["Update your firewall rules", "Use 2FA", "Upgrade to SSL"]
    return jsonify(suggestions)

# Schedule a patch
@app.route('/schedule-patch', methods=['POST'])
@login_required
def schedule_patch():
    data = request.get_json()
    patch_time = datetime.datetime.strptime(data.get('patch_time'), '%Y-%m-%d %H:%M:%S')
    scheduled_patches.append({
        'client': data.get('client'),
        'email': data.get('email'),
        'patch_time': patch_time
    })
    return jsonify({"message": "Patch scheduled successfully!"})

# Payment integration using Stripe
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'VulnGuard Pro Plan',
                    },
                    'unit_amount': 9900,
                },
                'quantity': 1,
            }],
            mode='subscription',
            success_url=url_for('success', _external=True),
            cancel_url=url_for('cancel', _external=True),
        )
        return jsonify(id=session.id)
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route('/success')
def success():
    return jsonify({"message": "Payment successful!"})

@app.route('/cancel')
def cancel():
    return jsonify({"message": "Payment canceled."})

# AI-driven threat detection placeholder
@app.route('/ai-threat-detection', methods=['GET'])
@login_required
def ai_threat_detection():
    threats = ["Potential SQL Injection detected", "XSS vulnerability found"]
    return jsonify(threats)

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

# Protect the admin route
@app.route('/admin-dashboard')
@login_required
def admin_dashboard():
    if current_user.id == 'admin':
        return jsonify({"message": "Welcome, Admin!"})
    else:
        return jsonify({"error": "Access denied"}), 403

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)