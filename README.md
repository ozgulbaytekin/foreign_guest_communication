# Foreign Guest Reminder System
##OVERVIEW
The Foreign Guest Reminder System is a web application designed to manage and send notifications about residence permit expiration dates for foreign guests. The system allows users to set expiration dates, receive automatic reminder emails, and manage notifications through a user-friendly interface.


##FEATURES
*Automatic Reminders: Sends email reminders to users and foreign guests about upcoming residence permit expiration dates.
*Notification Settings: Allows users to configure notification times, days and the email adresses to be notification sends.
*Guest Management: Add, edit, and delete guest records.
*Mass Mailing: Send announcements to all guests listed in the system.

##INSTALATION
###Prerequisites:
Python 3.6 or higher
Flask
Docker (optional, for containerized deployment)
A GitHub account (for version control and repository management)

###Install Dependencies
pip install -r requirements.txt

###Running the Application
1-) Without Docker: Start the Flask application:
'''bash
python app.py

Access the application at http://localhost:5000.

2-) With Docker: Build and run the Docker container:
'''bash
docker-compose up --build
'''

##CONFIGURATION:
Email Settings: Configure your email settings in the .env file for sending notifications.
Update flask secret key with using flask_secret_key.py


##USAGE
Add Guest: Use the form to add new guest records.
Edit Guest: Edit existing guest records from the table.
Delete Guest: Remove guest records as needed.
Send Notifications: Configure notification settings to manage when reminders are sent.


##CONTACT
For any questions or issues, please contact Ozgul Baytekin.
