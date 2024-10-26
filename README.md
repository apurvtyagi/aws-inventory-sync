# AWS Resource Sync to MongoDB

## Overview

This project is designed to sync AWS resources and load the data into a MongoDB database. It utilizes the Boto3 library to interact with AWS APIs and fetch comprehensive information about the specified resources. The project is built to be modular, allowing for easy addition of new AWS services.

## Features

- Syncs AWS resources such as EC2 instances and S3 buckets data to MongoDB.
- Retrieves detailed information about each resource, including various configurations (e.g., versioning, logging, ACLs).
- Supports pagination and error handling with retry mechanisms.
- Configurable through a YAML file to define the AWS regions, resources to sync, and MongoDB connection details.

## Installation

### Prerequisites

- Python 3.6 or higher
- MongoDB instance running locally or remotely
- AWS account with appropriate permissions to access resources

### Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/aws-mongo-sync.git
   cd aws-mongo-sync
   ```

2. **Install required packages:**

    You can use pip to install the necessary packages:  
    ```bash
    pip install boto3 pymongo pyyaml
    ```

3. **Configure AWS credentials:**

    Ensure your AWS credentials are configured. You can do this using the AWS CLI:
    ```bash
    aws configure
    ```
    Provide your AWS Access Key, Secret Access Key, region, and output format.


4. **Update the configuration file:**

    Modify the ```config.yml``` file to specify the desired AWS resources, MongoDB URI, and any additional settings.

**Usage:**

To run the synchronization script, execute the following command:  
    
    python main.py

The script will connect to AWS, fetch the specified resources, and insert or update the records in the MongoDB database.

**Configuration Example:**
The ```config.yml``` file should look like this:

```yaml
kind: source
spec:
  name: aws
  path: inhouse/aws
  registry: inhouse
  version: "v1.0.0"
  tables:
    - ec2_instances
    - s3_buckets
  destinations:
    - mongodb
  spec:
    aws_debug: false
    org:
      admin_account:
        local_profile: "<NAMED_PROFILE>"
      member_role_name: "OrganizationAccountAccessRole"
    regions:
      - "*"
    concurrency: 50
    initialization_concurrency: 4
    max_retries: 10
    max_backoff: 30
    table_options:
      aws_ec2_instances:
        filters:
          instance_states:
            - running
            - stopped
      aws_s3_buckets:
        filters:
          tag: environment
    mongo:
      uri: "mongodb://localhost:27017"
      database: "cloud_inventory"
      collection_prefix: "aws_"
```
