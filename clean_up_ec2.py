#!/usr/bin/env python3
"""
Cleanup script for the EC2 deployment.
Reads deploy_resources.json and config.json, then terminates the instance
and deletes the security group (if it was created by the deploy script).
"""

import json
import sys
import logging
import os
import boto3
from botocore.exceptions import ClientError

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

STATE_FILE = "deploy_resources.json"
CONFIG_FILE = "config.json"

def load_config():
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error(f"Failed to load config file: {e}")
        sys.exit(1)

def load_resources():
    if not os.path.exists(STATE_FILE):
        logger.error(f"State file {STATE_FILE} not found. Nothing to clean.")
        sys.exit(1)
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def cleanup():
    config = load_config()
    resources = load_resources()

    session = boto3.Session(
        aws_access_key_id=config['aws_access_key_id'],
        aws_secret_access_key=config['aws_secret_access_key'],
        region_name=resources.get('region', config.get('region', 'us-east-1'))
    )
    ec2 = session.resource('ec2')
    ec2_client = session.client('ec2')

    instance_id = resources.get('instance_id')
    if instance_id:
        try:
            instance = ec2.Instance(instance_id)
            logger.info(f"Terminating instance {instance_id}...")
            instance.terminate()
            instance.wait_until_terminated()
            logger.info("Instance terminated.")
        except ClientError as e:
            logger.error(f"Error terminating instance: {e}")

    created_sg_id = resources.get('created_sg_id')
    if created_sg_id:
        try:
            logger.info(f"Deleting security group {created_sg_id}...")
            ec2_client.delete_security_group(GroupId=created_sg_id)
            logger.info("Security group deleted.")
        except ClientError as e:
            logger.error(f"Error deleting security group: {e}")

    os.remove(STATE_FILE)
    logger.info(f"Removed {STATE_FILE}.")

if __name__ == "__main__":
    cleanup()