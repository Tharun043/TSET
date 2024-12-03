import os
import time
import imaplib
import email
from email.header import decode_header
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv

load_dotenv()

def extract_otp_from_html(body):
    soup = BeautifulSoup(body, "html.parser")
    otp_tag = soup.find("h1")  # Adjust based on your email structure
    if otp_tag:
        otp = otp_tag.get_text(strip=True)
        if otp.isdigit() and len(otp) == 6:
            return otp
    return None

def get_otp_from_email():
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("SENDER_PASSWORD")
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(EMAIL, PASSWORD)
    except Exception as e:
        print(f"Failed to connect to the email server: {e}")
        return None

    try:
        imap.select("inbox")
        status, messages = imap.search(None, 'X-GM-RAW "subject:Your OTP for TRIEC Mentoring Partnership"')

        if status == "OK" and messages[0]:
            latest_email_id = messages[0].split()[-1]
            status, msg_data = imap.fetch(latest_email_id, "(RFC822)")

            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    for part in msg.walk():
                        if part.get_content_type() in ["text/plain", "text/html"]:
                            body = part.get_payload(decode=True).decode()
                            otp = extract_otp_from_html(body)
                            if otp:
                                print("Extracted OTP:", otp)
                                return otp
        else:
            print("No matching emails found.")
    except Exception as e:
        print(f"Error fetching OTP: {e}")
    finally:
        imap.close()
        imap.logout()

    return None

def enter_otp_on_website(url, delay):
    time.sleep(delay)  # Add delay before opening the website
    EMAIL = os.getenv("EMAIL")
    options = Options()
    options.headless = False
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get(url)
        time.sleep(2)

        email_input = driver.find_element(By.CSS_SELECTOR, "#email")
        email_input.clear()
        email_input.send_keys(EMAIL)

        verify_button = driver.find_element(By.CSS_SELECTOR, "#button")
        verify_button.click()
        time.sleep(10)  # Adjust this if page loads faster

        otp = get_otp_from_email()
        if otp:
            otp_input = driver.find_element(By.CLASS_NAME, "frm-control")
            otp_input.clear()
            otp_input.send_keys(otp)

            submit_button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-black")
            submit_button.click()
            time.sleep(3)

            resume_button = driver.find_element(By.CSS_SELECTOR, ".btn.btn-orange")
            resume_button.click()
            time.sleep(3)
            print(f"Resume upload successful for URL: {url}")
        else:
            print(f"Failed to fetch OTP for URL: {url}")
            send_failure_email()

    except Exception as e:
        print(f"Error processing URL {url}: {e}")
    finally:
        driver.quit()

def send_failure_email():
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    subject = "TRIEC Response Check Failed"
    body = f"""
    <body style="margin: 10px; padding: 10px; text-align: left;">
        <div style="background-color: #c2ebed; width: 50%; padding: 20px; border-radius: 10px;">
            <p>Dear Team,</p>
            <p>The TRIEC check failed. Please investigate the issue.</p>
            <p>Last Checked: <strong>{current_time}</strong></p>
            <br>
            <b style="color: red;">Immediate attention is required.</b>
            <br><br>
            <p>Thanks,<br>Monitoring Team<br>DTSKILL Inc</p>
        </div>
    </body>
    """
    SMTP_SERVER = os.getenv("SMTP_SERVER")
    SMTP_PORT = os.getenv("SMTP_PORT")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
    RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'html'))

    try:
        with smtplib.SMTP(SMTP_SERVER, int(SMTP_PORT)) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        print("Failure email sent.")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    urls = [os.getenv("CRM_URL"), os.getenv("CRM_URL3")]
    with ThreadPoolExecutor(max_workers=len(urls)) as executor:
        # Add incremental delay for each URL
        delays = [i * 5 for i in range(len(urls))]  # 5 seconds apart
        executor.map(enter_otp_on_website, urls, delays)
