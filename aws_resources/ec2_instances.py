import boto3
from botocore.exceptions import ClientError
import time

def fetch_data(region, filters=None, max_retries=5, max_backoff=30):
    ec2_client = boto3.client("ec2", region_name=region)
    print('Fetching EC2 data')
    
    instances = []
    next_token = None
    
    for attempt in range(max_retries):
        try:
            if next_token:
                response = ec2_client.describe_instances(NextToken=next_token)
            else:
                response = ec2_client.describe_instances()

            for reservation in response["Reservations"]:
                for instance in reservation["Instances"]:
                    instance_info = {k: v for k, v in instance.items()}            
                    instance_info['region_cloudquery'] = region
                    try:
                        elastic_ips = ec2_client.describe_addresses(Filters=[{'Name': 'instance-id', 'Values': [instance_info["InstanceId"]]}])
                        if elastic_ips["Addresses"]:
                            instance_info["elastic_ip"] = elastic_ips["Addresses"][0].get("PublicIp")
                    except ClientError as e:
                        print(f"Error fetching Elastic IP for instance {instance_info['InstanceId']}: {e}")

                    instances.append(instance_info)

            next_token = response.get("NextToken")
            if not next_token:
                break

        except ClientError as e:
            print(f"Error fetching EC2 instances: {e}")
            if attempt < max_retries - 1:
                backoff_time = min(2 ** attempt, max_backoff)
                print(f"Retrying in {backoff_time} seconds...")
                time.sleep(backoff_time)
            else:
                print("Max retries exceeded. Exiting.")
                return []

    return instances
