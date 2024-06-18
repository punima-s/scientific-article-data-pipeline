"""Extracts the latest file"""
from os import environ
from datetime import datetime
from dotenv import load_dotenv
from boto3 import client


def get_s3_client() -> client:
    """Get client"""
    return client("s3", aws_access_key_id=environ["AWS_ACCESS_KEY"], aws_secret_access_key=environ["AWS_SECRET_KEY"])


def get_objects(s3_cli: client, bucket_name: str) -> list[str]:
    """Only get objects from the bucket under the folder: "c11-punima/" """
    return [(object['Key'], object['LastModified']) for object in s3_cli.list_objects(Bucket=bucket_name)['Contents']
            if 'c11-punima/' in object['Key'] and object['Size'] != 0]


def get_latest_file(objects: list) -> str:
    """Get the latest file. """
    latest_date = max([data[1] for data in objects])
    return [data for data in objects if data[1] == latest_date][0]


def generate_filename(date_value: datetime) -> str:
    """
    Generate a format name for the latest file being downloaded.
    PubmedArticle_date_min.xml
    """

    return f"PubmedArticle_{date_value.date()}_{date_value.minute}_{date_value.second}.xml"


def downloading_files(s3_cli: client, bucket_name: str, objects: list) -> None:
    """Downloading object files from the bucket in s3. """
    latest_file = get_latest_file(objects)
    if latest_file:
        new_file_name = generate_filename(latest_file[1])
        s3_cli.download_file(Bucket=bucket_name,
                             Key=latest_file[0], Filename=new_file_name)
    return None


def extract_main():
    """Main run of function for extracting file. """
    s3 = get_s3_client()
    input_bucket = environ['INPUT_BUCKET']
    try:
        file = get_objects(s3, input_bucket)
        downloading_files(s3, input_bucket, file)
    except ValueError:
        return {"Error: No files in this bucket!"}


if __name__ == "__main__":
    extract_main()
