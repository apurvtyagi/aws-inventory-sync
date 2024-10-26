import importlib
import boto3
from config import load_config
from mongo_db import connect_mongo, insert_data

def get_all_aws_regions():
    return ['us-east-1','ap-south-1']

def main():
    config = load_config()    
    mongo_client = connect_mongo(config["mongo"]["uri"])
    regions = config["spec"].get("regions", [])
    max_retries = config["spec"]["spec"].get("max_retries", [])
    max_backoff = config["spec"]["spec"].get("max_backoff", [])

    for table in config["spec"]["tables"]:
        resource_module_name = table
        resource_module_path = f"aws_resources.{resource_module_name}"
        
        try:
            resource_module = importlib.import_module(resource_module_path)            
            if '*' in regions:
                print(f"Wildcard '*' detected. Fetching all available AWS regions for {table}.")
                regions = get_all_aws_regions()
            else:
                regions = [regions] if isinstance(regions, str) else regions

            for region in regions:
                data = resource_module.fetch_data(region, filters=[], max_retries=max_retries, max_backoff=max_backoff)
                collection_name = f"{config['mongo']['collection_prefix']}{table}"
                insert_data(mongo_client, config["mongo"]["database"], collection_name, data)

                print(f"Successfully synced {table.upper()} data for region {region} to MongoDB")

        except ModuleNotFoundError:
            print(f"Module for resource '{table}' not found: {resource_module_path}")
        except Exception as e:
            print(f"Failed to sync {table.upper()}: {e}")

if __name__ == "__main__":
    main()
