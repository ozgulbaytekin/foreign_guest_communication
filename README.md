# Foreign Guest Reminder System

## Overview
The Foreign Guest Reminder System is a web application designed to manage and send notifications about residence permit expiration dates for foreign guests. The system allows users to set expiration dates, receive automatic reminder emails, and manage notifications through a user-friendly interface.

## Features
- **Automatic Reminders:** Sends email reminders to users and foreign guests about upcoming residence permit expiration dates.
- **Notification Settings:** Allows users to configure notification times, days, and the email addresses to which notifications are sent.
- **Guest Management:** Add, edit, and delete guest records.
- **Mass Mailing:** Send announcements to all guests listed in the system.

## INSTALLATION

### Prerequisites:
- Python 3.6 or higher
- Flask
- Docker (optional, for containerized deployment)
- A GitHub account (for version control and repository management)

### Install Dependencies:

``` bash 
pip install -r requirements.txt
```

## RUNNING THE APPLICATION:
### 1-) Without Docker
Start the Flask application:

``` bash 
python app.py
```

Access the application at http://localhost:5004.
### 2-) With Docker
Build and run the Docker container:

``` bash
docker-compose up --build
```

## CONFIGURATION
Email Settings: Configure admin email settings in the notification settings tab for sending perodical notifiactions and mass mails. You can add extra email addresses to send the expiratioon notification email and mass mails for announcments.

Flask Secret Key: Update Flask secret key using flask_secret_key.py.



## USAGE
Add Guest: Use the form to add new guest records.
Edit Guest: Edit existing guest records from the table.
Delete Guest: Remove guest records as needed.
Send Notifications: Configure notification settings to manage when reminders are sent.
Send mass mail: Make announcement to the recorded email addresses from the guests.json file.


## CONTACT
For any questions or issues, please contact Ozgul Baytekin.
