#!/usr/bin/env python
# encoding: utf-8

import json
import datetime
import requests
import boto3
#import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Slack の設定
#SLACK_POST_URL = os.environ['slackPostURL']
SLACK_POST_URL = "https://hooks.slack.com/services/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"
#SLACK_CHANNEL = os.environ['slackChannel']
SLACK_CHANNEL = "#test"

response = boto3.client('cloudwatch', region_name='us-east-1')

get_metric_statistics = response.get_metric_statistics(
    Namespace='AWS/Billing',
    MetricName='EstimatedCharges',
    Dimensions=[
        {
            'Name': 'Currency',
            'Value': 'USD'
        }
    ],
    StartTime=datetime.datetime.today() - datetime.timedelta(days=1),
    EndTime=datetime.datetime.today(),
    Period=86400,
    Statistics=['Maximum'])

cost = get_metric_statistics['Datapoints'][0]['Maximum']
date = get_metric_statistics['Datapoints'][0]['Timestamp'].strftime('%Y年%m月%d日')


##########################
#追記

num_get_metric_statistics = response.get_metric_statistics(
    Namespace='AWS/Billing',
    MetricName='EstimatedCharges',
    Dimensions=[
        {
            'Name': 'Currency',
            'Value': 'USD'
        },
        {
            'Name': 'ServiceName',
            'Value': 'AWSDataTransfer'
        }
    ],
    StartTime=datetime.datetime.today() - datetime.timedelta(days=1),
    EndTime=datetime.datetime.today(),
    Period=86400,
    Statistics=['Maximum'])

trans = num_get_metric_statistics['Datapoints'][0]['Maximum']

#ここまで
############################
#EC2
ec2_get_metric_statistics = response.get_metric_statistics(
    Namespace='AWS/Billing',
    MetricName='EstimatedCharges',
    Dimensions=[
        {
            'Name': 'Currency',
            'Value': 'USD'
        },
        {
            'Name': 'ServiceName',
            'Value': 'AmazonEC2'
        }
    ],
    StartTime=datetime.datetime.today() - datetime.timedelta(days=1),
    EndTime=datetime.datetime.today(),
    Period=86400,
    Statistics=['Maximum'])

ec2 = ec2_get_metric_statistics['Datapoints'][0]['Maximum']
############################

def build_message(cost):
    if float(cost) >= 10.0:
        color = "#ff0000" #red
    elif float(cost) > 0.0:
        color = "warning" #yellow
    else:
        color = "good"    #green

#    text = "%sまでのAWSの料金は、$%sです。" % (date, cost)

#    atachements = {"text":text,"color":color}

    atachements = {
                "fallback": "Required plain-text summary of the attachment.",
                "color": "#2eb886",
#                "pretext": "今日までのAWS料金・・・",
#                "author_name": "Bobby Tables",
#                "author_link": "http://flickr.com/bobby/",
#                "author_icon": "http://flickr.com/icons/bobby.jpg",
                "title": "%sまでのAWS料金" % (date),
#                "title_link": "https://api.slack.com/",
                "text": "総額$%s" % (cost),


        "fields": [
                    {
                        "title": "AWSDataTransfer",
                        "value": "$%s" %(trans),
                        "short": "fault"
                    },{
                        "title": "AmazonEC2",
                        "value": "$%s" %(ec2),
                        "short": "fault"
                    }
                ]
#                "image_url": "http://my-website.com/path/to/image.jpg",
#                "thumb_url": "http://example.com/path/to/thumb.png",
#                "footer": "Slack API",
#                "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
#                "ts": 123456789
    }

    return atachements

def lambda_handler(event, context):
    content = build_message(cost)

    # SlackにPOSTする内容をセット
    slack_message = {
        'channel': SLACK_CHANNEL,
        "attachments": [content],
    }

    # SlackにPOST
    try:
        req = requests.post(SLACK_POST_URL, data=json.dumps(slack_message))
        logger.info("Message posted to %s", slack_message['channel'])
    except requests.exceptions.RequestException as e:
        logger.error("Request failed: %s", e)
