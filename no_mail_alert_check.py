import requests,os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
# Website End points goes here
CRM_URL = os.getenv("CRM_URL")
CRM_URL2= os.getenv("CRM_URL2")
CRM_URL3= os.getenv("CRM_URL3")
CRM_URL4= os.getenv("CRM_URL4")
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = os.getenv("SMTP_PORT")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD") 
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")
CC_EMAIL = os.getenv("CC_EMAIL")


 
def check_and_notify(responses, environment_name):
    """
    Checks the status codes of responses and sends a failure email if any response fails.
    """
    failed = []
    for i, response in enumerate(responses, start=1):
        if response.status_code != 200:
            failed.append(f"Response {i} failed with status code: {response.status_code}")
    
    if failed:
        # Combine all failed messages for the email body
        error_message = f"{environment_name} check failed:\n" + "\n".join(failed)
        print(error_message)
        send_failure_email(error_message)
    else:
        print(f"{environment_name} is running smoothly. All status codes are 200.")

def send_failure_email(error):
    """
    Sends an email to notify about a failure.
    """
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = "TRIEC Response Check Failed"
    body = f"""
    <body style="margin: 10px; padding: 10px; text-align: left;">
        <div style="background-color: #c2ebed; width: 50%; padding: 20px; border-radius: 10px;">
            <p>Dear Team,</p> 
            <p>
                The TRIEC check failed with the following error: <strong>{error}</strong>
            </p> <br>
            <p>Last Checked: <strong>{current_time}</strong></p><br>
            <br>
            <b style="color: red;">Please check if there is an issue in the system.</b>
            <br><br>
            <p>Thanks and Regards,<br>
            <strong>Monitoring Team</strong><br>
            <strong>DTSKILL Inc</strong></p>
        </div>
    </body>
    """

    # Email Composition
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['CC'] = CC_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))  # Use 'html' to render the email correctly

    try:
        # Sending Email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print("Failure email sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def check_and_notify(urls, environment_name):
    """
    Checks the status codes of responses for a given environment.
    If any response fails, sends a failure email and continues to check the others.
    """
    for i, url in enumerate(urls, start=1):
        try:
            response = requests.get(url)
            if response.status_code != 200:
                error_message = f"{environment_name} - '{url}' failed with status code: {response.status_code}"
                print(error_message)
                send_failure_email(error_message)
            else:
                print(f"{environment_name} - '{url}' is running smoothly. Status Code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            error_message = f"{environment_name} - '{url}' encountered an error: {str(e)}"
            print(error_message)
            send_failure_email(error_message)


if __name__ == "__main__":
    try:
        # QA Environment
        qa_urls = [CRM_URL, CRM_URL2]
        check_and_notify(qa_urls, "Triec-QA-Mentor & Mentee")

        # UAT Environment
        uat_urls = [CRM_URL3, CRM_URL4]
        check_and_notify(uat_urls, "Triec-UAT-Mentor & Mentee")
    
    except Exception as e:
        # Global exception handling for unforeseen errors
        print(f"Critical error: {e}")
        send_failure_email(f"Critical error occurred: {str(e)}")