from flask import Flask, request, jsonify, redirect, url_for, flash, render_template
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import schedule
import time
from datetime import datetime, timedelta
from mass_mailing import mass_mailing_bp  # Import the blueprint
import logging
import threading

logging.basicConfig(level=logging.DEBUG)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')  # Use env var for secret key

# Register the Blueprint
app.register_blueprint(mass_mailing_bp)

GUESTS_FILE_PATH = 'guests.json'
NOTIFICATION_SETTINGS_FILE_PATH = 'notification_settings.json'


def parse_time_12_to_24(time_str):
    """Convert 12-hour time format (HH:MM AM/PM) to 24-hour format (HH:MM)."""
    try:
        return datetime.strptime(time_str, "%I:%M %p").strftime("%H:%M")
    except ValueError as e:
        logging.error("Error parsing time: %s", e)
        return None
    


@app.route('/add_email', methods=['GET','POST'])
def add_email():
    new_email = request.form['newEmail']
    
    # Load the current notification settings
    with open('notification_settings.json', 'r') as f:
        data = json.load(f)
    
    # Add the new email to the 'emails' list or create it if it doesn't exist
    if 'emails' not in data:
        data['emails'] = []
    
    data['emails'].append(new_email)
    
    # Save the updated settings back to the JSON file
    with open('notification_settings.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    return redirect(url_for('notification_time'))



def load_notification_settings():
    """Load notification settings from a JSON file, ensuring all expected keys are present."""
    try:
        with open(NOTIFICATION_SETTINGS_FILE_PATH, 'r') as f:
            settings = json.load(f)
            # Ensure all required keys are present, using defaults if missing
            if 'notification_time' not in settings:
                settings['notification_time'] = '12:00'  # Default to '12:00' if not set
            if 'reminder_days' not in settings:
                settings['reminder_days'] = {}  # Default to empty dictionary if not set
            return settings
    except FileNotFoundError:
        # Handle the case where the file is not found
        return {'notification_time': '12:00', 'reminder_days': {}}  # Default values
    except json.JSONDecodeError:
        # Handle JSON decode error
        return {'notification_time': '12:00', 'reminder_days': {}}  # Default values






def save_notification_settings(settings):
    """Save notification settings to the JSON file."""
    try:
        with open(NOTIFICATION_SETTINGS_FILE_PATH, 'w') as file:
            json.dump(settings, file, indent=4)
        print("Notification settings successfully saved.")
    except Exception as e:
        print(f"Error saving notification settings: {e}")







def send_email(to_email, subject, message):
    sender_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(message, 'plain'))

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
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.send_message(msg)
        print(f"Email sent to {to_email}.")
    except smtplib.SMTPException as e:
        print(f"Failed to send email to {to_email}: {e}")



def load_guests():
    """Load guest data from a JSON file."""
    if os.path.exists(GUESTS_FILE_PATH):
        try:
            with open(GUESTS_FILE_PATH, 'r') as file:
                data = json.load(file)
                return data if isinstance(data, list) else []
        except (json.JSONDecodeError, EOFError) as e:
            print(f"Error loading guests: {e}")
            return []
    return []

def save_guests(data):
    """Save guest data to a JSON file."""
    try:
        with open(GUESTS_FILE_PATH, 'w') as file:
            json.dump(data, file, indent=4)
        print("Guests data successfully saved to JSON file.")
    except Exception as e:
        print(f"Error saving guests data: {e}")

def schedule_reminders():
    """Schedule reminders based on the guest data and notification settings."""
    settings = load_notification_settings()
    reminder_days = settings.get('reminder_days', {})
    additional_emails = settings.get('emails', [])
    guests = load_guests()
    now = datetime.now()
    admin_email = os.getenv("EMAIL_ADDRESS")

    logging.info("Running schedule_reminders at %s", now.strftime("%Y-%m-%d %H:%M:%S"))

    for guest in guests:
        expiration_date = guest['expiration_date']
        guest_email = guest['email']
        guest_full_name = f"{guest['name']} {guest['surname']}"

        try:
            expiration = datetime.strptime(expiration_date, "%Y/%m/%d")

            for reminder_name, days_before in reminder_days.items():
                reminder_date = expiration - timedelta(days=days_before)
                logging.debug("Checking reminder: %s for guest: %s (expiration: %s, reminder_date: %s)", 
                              reminder_name, guest_full_name, expiration_date, reminder_date.strftime("%Y-%m-%d"))

                if now.date() == reminder_date.date():
                    logging.info("Sending %d-day reminder to %s", days_before, guest_email)
                    
                    # Send email to guest
                    send_email(guest_email, f"{days_before} Days Reminder", f"Dear {guest_full_name}, your permit will expire in {days_before} days!")
                    
                    # Send email to admin
                    send_email(admin_email, f"Admin Notification: {days_before} Days Reminder", f"{guest_full_name}'s permit will expire in {days_before} days.")
                    
                    # Send email to additional email addresses
                    for additional_email in additional_emails:
                        send_email(additional_email, f"Notification: {days_before} Days Reminder", f"{guest_full_name}'s permit will expire in {days_before} days.")
                else:
                    logging.debug("No email sent for reminder: %s (now: %s, reminder_date: %s)", 
                                  reminder_name, now.date(), reminder_date.date())
        except ValueError as e:
            logging.error("Error parsing date for %s: %s", guest_full_name, e)


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        expiration_date = request.form.get('expiration_date')

        if not name or not surname or not email or not expiration_date:
            flash('All fields are required!')
            return redirect(url_for('index'))

        guests = load_guests()
        new_id = max([guest['id'] for guest in guests], default=-1) + 1

        guest_data = {
            'id': new_id,
            'name': name,
            'surname': surname,
            'email': email,
            'expiration_date': expiration_date
        }

        guests.append(guest_data)
        save_guests(guests)

        flash('Information successfully saved!')
        return redirect(url_for('index'))

    guests = load_guests()
    return render_template('index.html', guests=guests)

@app.route('/add_guest', methods=['POST'])
def add_guest():
    data = request.get_json()
    name = data.get('name')
    surname = data.get('surname')
    email = data.get('email')
    expiration_date = data.get('expiration_date')

    # Convert date format from y-m-d to y/m/d
    formatted_date = expiration_date.replace('-', '/')

    if not name or not surname or not email or not expiration_date:
        return jsonify({'success': False, 'message': 'All fields are required!'})

    guests = load_guests()
    new_id = max([guest['id'] for guest in guests], default=-1) + 1

    guest_data = {
        'id': new_id,
        'name': name,
        'surname': surname,
        'email': email,
        'expiration_date': formatted_date  # Save formatted date
    }

    guests.append(guest_data)
    save_guests(guests)

    return jsonify({'success': True, 'message': 'Guest added successfully!'})

def update_guest_info(guest_id, name, surname, email, expiration_date):
    guests = load_guests()

    for guest in guests:
        if guest['id'] == guest_id:
            guest['name'] = name
            guest['surname'] = surname
            guest['email'] = email
            guest['expiration_date'] = expiration_date
            save_guests(guests)
            return True

    return False

@app.route('/update_guest', methods=['POST'])
def update_guest():
    try:
        data = request.get_json()
        guest_id = int(data.get('id'))
        name = data.get('name')
        surname = data.get('surname')
        email = data.get('email')
        expiration_date = data.get('expiration_date')

        update_successful = update_guest_info(guest_id, name, surname, email, expiration_date)

        if update_successful:
            return jsonify({"success": True})
        else:
            return jsonify({"success": False, "error": "Guest not found."}), 404
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/delete_guest/<int:guest_id>', methods=['POST'])
def delete_guest(guest_id):
    guests = load_guests()
    guest_to_delete = next((guest for guest in guests if guest['id'] == guest_id), None)

    if guest_to_delete:
        guests.remove(guest_to_delete)
        save_guests(guests)
        flash('Guest record deleted successfully!')
    else:
        flash('Guest record not found.')
    
    return redirect(url_for('index'))

@app.route('/notification_time', methods=['GET', 'POST'])
def notification_time():
    if request.method == 'POST':
        notification_time = request.form['notification_time']
        try:
            update_scheduler_time(notification_time)
            flash('Notification time updated successfully!')
        except ValueError:
            flash('Invalid time format. Please enter a valid time in HH:MM AM/PM format.')

    notification_settings = load_notification_settings()
    current_notification_time = notification_settings.get('notification_time', '12:00')  # Default to '12:00' if not set

    return render_template('notification_settings.html', settings=notification_settings, notification_time=current_notification_time)


@app.route('/update_notification_days', methods=['GET','POST'])
def update_notification_days():
    try:
        reminder_days = request.form.getlist('reminder_days[]')  # Get list of reminder days from the form
        # Convert the reminder_days list into a dictionary format to store in the settings
        reminder_days_dict = {f"Reminder {i+1}": int(day) for i, day in enumerate(reminder_days)}

        settings = load_notification_settings()
        settings['reminder_days'] = reminder_days_dict
        save_notification_settings(settings)
        flash('Reminder days updated successfully!')
    except ValueError as e:
        flash(f"Error updating reminder days: {e}")
    except Exception as e:
        flash(f"An unexpected error occurred: {e}")

    return redirect(url_for('notification_time'))

def update_scheduler_time(time_str):
    # Validate the time format (optional, but recommended)
    if not re.match(r'^(0[1-9]|1[0-2]):[0-5][0-9] [APap][Mm]$', time_str):
        raise ValueError("Invalid time format. Expected HH:MM AM/PM")

    settings = load_notification_settings()
    settings['notification_time'] = time_str  # Store in HH:MM AM/PM format
    save_notification_settings(settings)
    
    # Convert to 24-hour format for scheduling
    time_24 = parse_time_12_to_24(time_str)
    if not time_24:
        raise ValueError("Invalid time format during conversion")

    # Restart the schedule with the new time
    schedule.clear()
    schedule_time = f"{time_24}:00"
    schedule.every().day.at(schedule_time).do(schedule_reminders)

    logging.info("Scheduler updated with new time: %s", schedule_time)



def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

import re

if __name__ == '__main__':
    # Schedule tasks
    settings = load_notification_settings()
    schedule_time = settings.get('notification_time', '12:00')  # Default to '12:00' in 24-hour format if not set



    # Start the scheduler in a new thread
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True  # Ensures the thread exits when the main program exits
    scheduler_thread.start()

    app.run(debug=True, host='0.0.0.0', port=5004)

