import json
import random

import boto3
import requests


def query_bap(url, api_key, dataset_id, cis):
    headers = {
        "x-api-key": api_key,
        "id-type": "ci",
    }

    data = {
        "dataset_id": dataset_id,
        "ids": cis,
    }
    data = json.dumps(data)

    res = requests.post(url, headers=headers, data=data)

    return res


def call_bap_api(url, api_key, dataset_id, cis):
    headers = {
        "x-api-key": api_key,
        "id-type": "ci",
    }

    data = {
        "dataset_id": dataset_id,
        "ids": cis,
    }

    res = requests.post(url, headers=headers, json=data)

    return (url, headers, data, res)


def publish_to_lunar(
    dic,
    event_stream_producer_role_arn="arn:aws:iam::891689049562:role/service-role/lunar-recipe-event-stream-aidp-role",
):
    sts_client = boto3.client("sts")

    assumed_role_object = sts_client.assume_role(
        RoleArn=event_stream_producer_role_arn,
        RoleSessionName="test-session",
    )

    credentials = assumed_role_object["Credentials"]

    kinesis = boto3.client(
        "kinesis",
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
    )

    response = kinesis.put_record(
        StreamName="lunar-recipe-event-stream",
        Data=json.dumps(dic, ensure_ascii=False),
        PartitionKey=str(random.randint(0, 500)),
    )

    return response
