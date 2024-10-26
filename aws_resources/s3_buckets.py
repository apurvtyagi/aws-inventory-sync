import boto3
from botocore.exceptions import ClientError
import time

def fetch_data(region, filters=None, max_retries=5, max_backoff=30):
    s3_client = boto3.client("s3", region_name=region)
    print('Fetching S3 data')
    
    buckets = []

    for attempt in range(max_retries):
        try:
            response = s3_client.list_buckets()
            break  # Exit the retry loop if successful
        except ClientError as e:
            print(f"Error fetching S3 buckets: {e}")
            if attempt < max_retries - 1:
                backoff_time = min(2 ** attempt, max_backoff)
                print(f"Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
            else:
                print("Max retries exceeded. Exiting.")
                return []

    for bucket in response["Buckets"]:
        bucket_name = bucket["Name"]
        
        bucket_info = {k: v for k, v in bucket.items()}            
        bucket_info['region_cloudquery'] = region   

        # Get the location of the bucket with retry logic
        for attempt in range(max_retries):
            try:
                bucket_location = s3_client.get_bucket_location(Bucket=bucket_name)
                bucket_info["location"] = bucket_location["LocationConstraint"]
                break  # Exit the retry loop if successful
            except ClientError as e:
                print(f"Error fetching location for bucket {bucket_name}: {e}")
                if attempt < max_retries - 1:
                    backoff_time = min(2 ** attempt, max_backoff)
                    print(f"Retrying in {backoff_time} seconds...")
                    time.sleep(backoff_time)
                else:
                    bucket_info["location"] = "Error fetching location: " + str(e)

        # Get versioning configuration
        try:
            versioning = s3_client.get_bucket_versioning(Bucket=bucket_name)
            bucket_info["versioning"] = versioning.get("Status", "Not Enabled")
        except ClientError as e:
            bucket_info["versioning"] = "Error fetching versioning: " + str(e)

        # Get logging configuration
        try:
            logging = s3_client.get_bucket_logging(Bucket=bucket_name)
            bucket_info["logging"] = logging.get("LoggingEnabled", "Logging is not enabled")
        except ClientError as e:
            bucket_info["logging"] = "Error fetching logging: " + str(e)

        # Get lifecycle configuration
        try:
            lifecycle = s3_client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
            bucket_info["lifecycle"] = lifecycle["Rules"]
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchLifecycleConfiguration':
                bucket_info["lifecycle"] = "No lifecycle configuration"
            else:
                bucket_info["lifecycle"] = "Error fetching lifecycle: " + str(e)

        # Get ACL (Access Control List)
        try:
            acl = s3_client.get_bucket_acl(Bucket=bucket_name)
            bucket_info["acl"] = acl["Grants"]
        except ClientError as e:
            bucket_info["acl"] = "Error fetching ACL: " + str(e)

        # Get tags
        try:
            tags = s3_client.get_bucket_tagging(Bucket=bucket_name)
            bucket_info["tags"] = tags.get("TagSet", [])
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchTagSet':
                bucket_info["tags"] = "No tags"
            else:
                bucket_info["tags"] = "Error fetching tags: " + str(e)

        # Append the bucket information to the list
        buckets.append(bucket_info)

    return buckets
