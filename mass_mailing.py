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

def send_mass_email(subject, message):
    sender_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

    guests = load_guests()

    for guest in guests:
        guest_email = guest['email']
        msg['To'] = guest_email

        try:
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()  # Upgrade to secure connection
                server.login(sender_email, password)
                server.send_message(msg)
            print(f"Announcement sent to {guest_email}.")
        except smtplib.SMTPException as e:
            print(f"Failed to send announcement to {guest_email}: {e}")

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
