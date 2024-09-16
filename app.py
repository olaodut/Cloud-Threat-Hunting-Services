from flask import Flask, jsonify
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)