from os import environ
from dotenv import load_dotenv
from extract_file import extract_main
from process import process_main
from upload_file import upload_main
from emailing import start_task_message, finished_task_message

if __name__ == "__main__":
    load_dotenv()
    sender_email = environ["SENDER_EMAIL"]
    receiver_email = environ["RECEIVER_EMAIL"]
    password = environ["PASSWORD"]
    start_task_message(sender_email, receiver_email, password)
    extract_main()
    process_main()
    upload_main()
    finished_task_message(sender_email, receiver_email, password)
