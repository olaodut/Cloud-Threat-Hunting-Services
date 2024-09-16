from flask import Flask, jsonify, request
import smtplib
from email.mime.text import MIMEText
import datetime
import time
from threading import Thread

app = Flask(__name__)

# Store scheduled patches (in-memory for simplicity)
scheduled_patches = []

# Email sending function
def send_email(subject, recipient, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'youremail@example.com'  # Replace with your email
    msg['To'] = recipient

    # Replace with your SMTP server details
    smtp_server = 'smtp.gmail.com'  # Gmail SMTP server example
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

if __name__ == '__main__':
    # Start the patch management process in the background
    patch_thread = Thread(target=apply_patches)
    patch_thread.daemon = True
    patch_thread.start()

    app.run(host='0.0.0.0', port=5000)