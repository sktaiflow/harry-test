import base64
import json

import boto3
from aws_kinesis_agg.deaggregator import iter_deaggregate_records


def parse_payload(payload):
    payload_decoded = base64.b64decode(payload).decode("utf8")
    payload_dict = json.loads(payload_decoded)
    return payload_dict


def parse_kinesis(event):
    for record in event["Records"]:
        a = record["kinesis"]["data"]
        b = base64.b64decode(a)
        c = b.decode("utf8")
        d = json.loads(c)
        yield d


def parse_kinesis_agg(event):
    for record in iter_deaggregate_records(event["Records"]):
        a = record["kinesis"]["data"]
        b = base64.b64decode(a)
        c = b.decode("utf8")
        d = json.loads(c)
        yield d


def get_kinesis_object_by_assume_role(assume_role_arn, region_name):
    sts_client = boto3.client("sts")

    assumed_role_object = sts_client.assume_role(
        RoleArn=assume_role_arn,
        RoleSessionName="kinesis_put_records",
    )

    credentials = assumed_role_object["Credentials"]

    kinesis = boto3.client(
        "kinesis",
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
        region_name=region_name,
    )

    return kinesis


def mq_parse_kinesis(event):
    for record in event["Records"]:
        a = record["kinesis"]["data"]
        b = base64.b64decode(a)
        temp_list = []
        for b in reversed(b):
            if b == 32:
                break
            else:
                temp_list.append(b)

        m_byte = list(reversed(temp_list))
        m_string = "".join(chr(i) for i in m_byte)
        m_list = m_string.split("|")
        d = {
            "svc_mgmt_num": m_list[0],
            "service_code": m_list[1],
            "usage_data": m_list[2],
            "event_time": m_list[3],
        }
        yield d
