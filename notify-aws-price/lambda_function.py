#!/usr/bin/env python
# encoding: utf-8

import json
import datetime
import requests
import boto3
import logging
import os

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Slack の設定

SLACK_POST_URL = os.environ["slackPostURL"]
SLACK_CHANNEL = os.environ["slackChannel"]
POST_TEXT = ""
POST_FIELDS = {
            "fields":[
                ]
            }

def calculate_billing(line):
    for item in line:
        response = boto3.client('cloudwatch', region_name='us-east-1')
        get_metric_statistics = response.get_metric_statistics(
            Namespace='AWS/Billing',
            MetricName='EstimatedCharges',
            Dimensions=[
                {
                    'Name': 'Currency',
                    'Value': 'USD'
                },
                {
                    'Name': 'ServiceName',
                    'Value': item
                }
            ],
        StartTime=datetime.datetime.today() - datetime.timedelta(days=1),
        EndTime=datetime.datetime.today(),
        Period=86400,
        Statistics=['Maximum'])

        cost = get_metric_statistics['Datapoints'][0]['Maximum']
        fields = {
                "title": item,
                "value": cost,
                "short": "false"
        }
        POST_FIELDS["fields"].append(fields)

    return POST_FIELDS["fields"]

def lambda_handler(event, context):
    #line = ["AmazonApiGateway","AmazonCloudWatch","AmazonDynamoDB","AmazonEC2","AmazonECR","AmazonS3","AmazonSNS","AWSCloudTrail","AWSConfig","AWSDataTransfer","AWSIoT","awskms","AWSLambda","AWSMarketplace","AWSQueueService"]
    line = ["AmazonApiGateway","AmazonCloudWatch","AmazonDynamoDB","AmazonEC2","AmazonECR","AmazonS3","AmazonSNS","AWSCloudTrail","AWSConfig","AWSDataTransfer","awskms","AWSLambda","AWSMarketplace","AWSQueueService"]

    res = calculate_billing(line)
    post_data = {"title": "AWS料金は....", "color": "good", "fields" : res}

    # SlackにPOSTする内容をセット
    slack_message = {
        'channel': SLACK_CHANNEL,
        "attachments": [post_data],
    }
    print(slack_message)

    # SlackにPOST
    try:
        req = requests.post(SLACK_POST_URL, data=json.dumps(slack_message))
        logger.info("Message posted to %s", slack_message['channel'])
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", e)

