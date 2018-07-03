#!/usr/bin/env python
# -*- coding: utf-8 -*-

import boto3
import datetime
import os
import time
from urllib.parse import parse_qs

# 使うモジュールを宣言
client = boto3.client('ec2')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ["table_name"])

# Spot request Specification
spot_price = "0.06"
instance_count = 1
request_type = "request"
duration_minutes = 360  # 360分経過で終了させる
valid_until = datetime.datetime.now() + datetime.timedelta(minutes=duration_minutes)
security_group_id = "sg-1c961c64"
instance_type = "c3.xlarge"
availability_zone = "ap-northeast-1a"
subnet_id = "subnet-2f7f7b66"
iam_profile_arn = "arn:aws:iam::474537151635:instance-profile/aws-opsworks-ec2-role"
iam_fleet_arn = "arn:aws:iam::474537151635:role/aws-ec2-spot-fleet-tagging-role"
token = "FxfMJOlXxNHNKUXn2jiT4cbx"

def lambda_handler(event, context):
    print(event)
    body_parse = parse_qs(event["body"])

    # Token authorize
    if body_parse["token"][0] != token:
        return {"error": "Invalid token"}

    info = table.get_item(
        Key={
            "Id": '1'
        }
    )['Item']

    image_id = info["latest_ami"]

    # start処理
    if body_parse["trigger_word"][0] == "start":

        if info['state'] == 'stop':
            # 起動するぞう

            response = client.request_spot_fleet(
                DryRun=False,
                SpotFleetRequestConfig={
                    "SpotPrice": spot_price,
                    "TargetCapacity": instance_count,
                    "Type": request_type,
                    "ValidUntil": valid_until.replace(microsecond=0),
                    "TerminateInstancesWithExpiration": True,
                    "IamFleetRole": iam_fleet_arn,
                    "LaunchSpecifications": [
                        {
                            "ImageId": image_id,
                            "SecurityGroups": [{
                                "GroupId": security_group_id
                            }],
                            "InstanceType": instance_type,
                            "Placement": {
                                "AvailabilityZone": availability_zone
                            },
                            "IamInstanceProfile": {
                                "Arn": iam_profile_arn
                            },
                            "SubnetId": subnet_id
                        }
                    ]

                }
            )
            spot = response
            print(spot)

            time.sleep(15)
            response = client.describe_spot_fleet_instances(
                DryRun=False,
                SpotFleetRequestId=response["SpotFleetRequestId"]
            )["ActiveInstances"][0]["InstanceId"]
            table.update_item(
                Key={
                    'Id': '1'
                },
                AttributeUpdates={
                    'state': {
                        'Action': 'PUT',
                        'Value': 'startup'
                    },
                    'expire': {
                        'Action': 'PUT',
                        'Value': valid_until.isoformat()
                    },
                    'requestId': {
                        'Action': 'PUT',
                        'Value': spot["SpotFleetRequestId"]
                    },
                    'InstanceId': {
                        'Action': 'PUT',
                        'Value': response
                    }
                }
            )
            return {
                "username": u"ねぷねぷ＠7D2D Server",
                "text": u"おっけー！今準備してるから、ちょっとだけ待ってね！"
            }
        else:
            if info['state'] == 'startup':
                return {
                    "username": u"ねぷねぷ＠7D2D Server",
                    "text": u"時間かかってるみたいかな……。もうちょっとで起動するはずだから、待っててね！"
                }

            if info['state'] == 'running':
                return {
                    "username": u"ねぷねぷ＠7D2D Server",
                    "text": u"ねぷぅ……？サーバはもう起動してるみたいだよ？"
                }

