from os import environ, remove
import glob
from boto3 import client
from dotenv import load_dotenv
from extract_file import get_s3_client


def get_csv_file():
    """Get the new csv file"""
    return glob.glob("Punima_*.csv")


def upload_csv(filename: str, bucket_name: str, s3_client: client):
    """upload csv """
    s3_client.upload_file(Filename=filename, Bucket=bucket_name,
                          Key=f"c11-punima/{filename}")


def upload_main():
    """Main run of functions to upload csv file to s3 bucket. """
    OUTPUT_BUCKET = environ["OUTPUT_BUCKET"]
    s3 = get_s3_client()
    csv_file = get_csv_file()[0]
    upload_csv(csv_file, OUTPUT_BUCKET, s3)
    remove(csv_file)


if __name__ == "__main__":
    load_dotenv()
    OUTPUT_BUCKET = environ["OUTPUT_BUCKET"]
    s3 = get_s3_client()
    csv_file = get_csv_file()[0]
    upload_csv(csv_file, OUTPUT_BUCKET, s3)
