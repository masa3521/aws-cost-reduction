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
#logger.setLevel(logging.DEBUG)

# Slack の設定i
# Slack の設定i
# Slack の設定i
# Slack の設定i

SLACK_POST_URL = os.environ["slackPostURL"]
#SLACK_POST_URL = "https://hooks.slack.com/services/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"
#SLACK_CHANNEL = "#test"
SLACK_CHANNEL = os.environ["slackChannel" ]
POST_TEXT = ""
POST_FIELDS = {
            "fields":[
                    #{"title": "","value": "","short": "false"}
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
        date = get_metric_statistics['Datapoints'][0]['Timestamp'].strftime('%Y年%m月%d日')
        fields = {
                "title": item,
                "value": cost,
                "short": "false"
        }
        POST_FIELDS["fields"].append(fields)

    print(POST_FIELDS["fields"])
    return POST_FIELDS["fields"]

def lambda_handler(event, context):
    line = ["AWSDataTransfer","AWSConfig","AmazonS3","AmazonEC2","AWSLambda"]
    #line = ["AmazonEC2", "AmazonRDS", "AmazonRoute53", "AmazonS3", "AmazonSNS", "AWSDataTransfer", "AWSLambda", "AWSQueueService"]

    res = calculate_billing(line)
    print(res)
    POST_TEXT2 = {"title": "AWS料金は....", "color": "good", "fields" : res}
    print(POST_TEXT2)

    # SlackにPOSTする内容をセット
    slack_message = {
        'channel': SLACK_CHANNEL,
        "attachments": [POST_TEXT2],
    }
    print(slack_message)

    # SlackにPOST
    try:
        req = requests.post(SLACK_POST_URL, data=json.dumps(slack_message))
        logger.info("Message posted to %s", slack_message['channel'])
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", e)

