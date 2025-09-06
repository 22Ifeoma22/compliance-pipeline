import os, smtplib
from email.message import EmailMessage

# Load environment variables
user = os.getenv("EMAIL_USER")
pwd  = os.getenv("EMAIL_PASS")

if not user or not pwd:
    print("❌ Missing EMAIL_USER or EMAIL_PASS environment variables")
    exit(1)

msg = EmailMessage()
msg["From"] = user
msg["To"] = user   # send to yourself first for testing
msg["Subject"] = "✅ Test Email from Python"
msg.set_content("Hello Brow,\n\nThis is a test email from your Python automation pipeline.\n\n– ChatGPT")

try:
    with smtplib.SMTP("smtp.office365.com", 587) as s:  # for Outlook/Office 365
        s.starttls()
        s.login(user, pwd)
        s.send_message(msg)
    print(f"✅ Test email sent to {user}")
except Exception as e:
    print(f"❌ Failed to send: {e}")
