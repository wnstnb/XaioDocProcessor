import os
import boto3
from io import BytesIO

# Initialize the S3 client using environment variables
s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name="us-east-1"  # Adjust if needed
)

def upload_fileobj_to_s3(file_obj, object_key, bucket_name="form-sage-storage"):
    """
    Upload a file-like object to S3.

    Args:
        file_obj: A file-like object (e.g., BytesIO) containing the file data.
        object_key: The key (path/filename) where the file should be stored in the bucket.
        bucket_name: The S3 bucket name. Defaults to "form-sage-storage".

    Returns:
        The S3 object key. You can optionally modify this to return a presigned URL.
    """
    s3_client.upload_fileobj(file_obj, bucket_name, object_key)
    return object_key

def download_fileobj_from_s3(object_key, bucket_name="form-sage-storage"):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
        region_name="us-east-1"  # Ensure this matches your bucket's region
    )
    response = s3_client.get_object(Bucket=bucket_name, Key=object_key)
    file_content = response['Body'].read()
    return BytesIO(file_content)
