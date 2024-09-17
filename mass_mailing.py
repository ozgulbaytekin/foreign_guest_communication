import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv
import json
from flask import Blueprint, request, redirect, url_for, flash, render_template

# Load environment variables from .env file
load_dotenv()

# Define the Blueprint
mass_mailing_bp = Blueprint('mass_mailing_bp', __name__)

GUESTS_FILE_PATH = 'guests.json'
NOTIFICATION_SETTINGS_FILE_PATH = 'notification_settings.json'

def load_notification_settings():
    """Load notification settings from a JSON file, ensuring all expected keys are present."""
    try:
        with open(NOTIFICATION_SETTINGS_FILE_PATH, 'r') as f:
            settings = json.load(f)
            # Ensure all required keys are present, using defaults if missing
            if 'smtp_email' not in settings:
                settings['smtp_email'] = ''  # Default to empty if not set
            if 'smtp_password' not in settings:
                settings['smtp_password'] = ''  # Default to empty if not set
            if 'emails' not in settings:
                settings['emails'] = []  # Default to empty list if not set
            return settings
    except FileNotFoundError:
        return {'notification_time': '12:00', 'reminder_days': {}, 'smtp_email': '', 'smtp_password': '', 'emails': []}
    except json.JSONDecodeError:
        return {'notification_time': '12:00', 'reminder_days': {}, 'smtp_email': '', 'smtp_password': '', 'emails': []}

def send_mass_email(subject, message):
    settings = load_notification_settings()
    sender_email = settings.get("smtp_email")
    password = settings.get("smtp_password")
    notification_emails = settings.get("emails", [])

    if not sender_email:
        print("SMTP email is not set in notification_settings.json")
        return

    guests = load_guests()
    recipient_emails = notification_emails + [guest['email'] for guest in guests]

    for recipient_email in recipient_emails:
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['Subject'] = subject
        msg.attach(MIMEText(message, 'plain'))
        msg['To'] = recipient_email

        if sender_email.endswith('@gmail.com'):
            smtp_server = 'smtp.gmail.com'
            smtp_port = 587
        elif sender_email.endswith('@outlook.com') or sender_email.endswith('@hotmail.com'):
            smtp_server = 'smtp.office365.com'
            smtp_port = 587
        else:
            print("Unsupported email domain.")
            return

        try:
            print(f"Connecting to SMTP server {smtp_server}...")
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, password)
                server.send_message(msg)
            print(f"Email sent to {recipient_email}.")
        except smtplib.SMTPAuthenticationError as e:
            print(f"Authentication error: {e}")
        except smtplib.SMTPException as e:
            print(f"Failed to send email to {recipient_email}: {e}")

def load_guests():
    if os.path.exists(GUESTS_FILE_PATH):
        try:
            with open(GUESTS_FILE_PATH, 'r') as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, EOFError) as e:
            print(f"Error loading guests: {e}")
            return []
    return []

@mass_mailing_bp.route('/mass_mailing', methods=['GET', 'POST'])
def mass_mailing():
    if request.method == 'POST':
        subject = request.form['subject']
        message = request.form['message']
        send_mass_email(subject, message)
        flash('Announcement successfully sent!')
        return redirect(url_for('mass_mailing_bp.mass_mailing'))

    return render_template('mass_mailing.html')
