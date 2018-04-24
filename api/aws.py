"""This module contains AWS integration utilities"""

import os
from uuid import uuid4
import boto3


if 'MINTAX_UPLOAD_BUCKET' not in os.environ:
    raise Exception('MINTAX_UPLOAD_BUCKET not specified')


def s3upload(data):
    """Uploads binary content to a S3 bucket, returning
    an uuid4 used as the identifier"""
    key = uuid4()
    s3cli = boto3.client('s3')
    s3cli.upload_fileobj(data, os.environ['MINTAX_UPLOAD_BUCKET'], str(key))
    return key


def s3download(key):
    """Downloads binary content from the S3 bucket by key"""
    s3cli = boto3.client('s3')
    response = s3cli.get_object(Bucket=os.environ['MINTAX_UPLOAD_BUCKET'], Key=str(key))
    return response['Body']
