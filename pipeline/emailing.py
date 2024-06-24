"""sends email notification."""
from os import environ
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv


def sending_email(sender_email: str, receiver_email: str, app_password: str, msg: MIMEText) -> None:
    """Sending the message to the email."""
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")


def start_task_message(sender_email: str, receiver_email: str, app_pw: str) -> None:
    """Curates message for starting a task."""
    subject = "AWS Task: Started"
    body = """New article data file has been add to the input bucket.
              So the task to extract, process and upload the file will begin now."""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    sending_email(sender_email, receiver_email, app_pw, msg)


def finished_task_message(sender_email: str, receiver_email: str, app_pw: str) -> None:
    """Curates message for finishing the task."""
    subject = "AWS Task: Finished"
    body = """New article data matched csv file has been add to the output bucket."""
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    sending_email(sender_email, receiver_email, app_pw, msg)


if __name__ == "__main__":
    load_dotenv()
    SENDER_EMAIL = environ["EMAIL"]
    RECEIVER_EMAIL = "trainee.punima.shahi@sigmalabs.co.uk"
    # Use the app-specific password generated
    APP_PASSWORD = environ["PASSWORD"]
    print(environ["EMAIL"])
