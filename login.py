import imaplib
import email
import re
import os
from email.header import decode_header
from bs4 import BeautifulSoup

def extract_otp_from_html(body):
    # Use BeautifulSoup to parse HTML content and find the OTP
    soup = BeautifulSoup(body, "html.parser")
    otp_tag = soup.find("h1")  # Find the <h1> tag containing the OTP
    if otp_tag:
        otp = otp_tag.get_text(strip=True)  # Extract text inside <h1> and remove extra spaces
        if otp.isdigit() and len(otp) == 6:
            return otp
    return None  # Return None if OTP not found

if __name__ == "__main__":
    # Retrieve email credentials from environment variables
    EMAIL = os.getenv("EMAIL")
    PASSWORD = os.getenv("PASSWORD")

    # Connect to the email server
    try:
        imap = imaplib.IMAP4_SSL("imap.gmail.com")
        imap.login(EMAIL, PASSWORD)
    except Exception as e:
        print(f"Failed to connect to the email server: {e}")
        exit()

    # Select the mailbox you want to check
    imap.select("inbox")

    # Search for emails that contain OTP in the subject line (case-insensitive search)
    status, messages = imap.search(None, 'X-GM-RAW "subject:Your OTP for TRIEC Mentoring Partnership"')

    # Get the latest email ID
    if status == "OK" and messages[0]:
        latest_email_id = messages[0].split()[-1]
        status, msg_data = imap.fetch(latest_email_id, "(RFC822)")

        # Extract OTP from the email
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == "text/plain":
                        body = part.get_payload(decode=True).decode()
                    elif content_type == "text/html":
                        # Extract text from HTML if no plain text part is found
                        body = part.get_payload(decode=True).decode()
                    else:
                        continue
                    
                    otp = extract_otp_from_html(body)  # Extract OTP using regex
                    if otp:
                        print("Extracted OTP:", otp)
                    else:
                        print("OTP not found in the email.")
    else:
        print("No matching emails found.")

    # Close the connection
    imap.close()
    imap.logout()
