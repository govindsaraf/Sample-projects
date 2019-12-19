#!/usr/bin/python

import boto3
import json
import sys
import os.path
from os import path
sys.path.insert(0, '../')
from common import *
import re
from re import search

#Global variables
client = boto3.client('cloudtrail')
varFlag = ''

def get_regions():
    client = boto3.client('ec2')
    region_response = client.describe_regions()
    regions = [region['RegionName'] for region in region_response['Regions']]
    return regions

def func_validate_and_update(varDecision):
    for n in get_regions():
        client = boto3.client('cloudtrail', region_name=n)
        response = client.describe_trails()
        S3_CLIENT = boto3.client('s3')
        temp = []
        for m in response['trailList']:
            if m['HomeRegion'] == n:
                #print (m['S3BucketName']+ ' :-----: ' +m['HomeRegion'])
                s3_response = S3_CLIENT.get_bucket_acl(Bucket=m['S3BucketName'])
                if varDecision is False:
                    if not re.search(r'(global/AllUsers|global/AuthenticatedUsers)', str(s3_response)):
                        print(m['S3BucketName'])
                        varBucketName = m['S3BucketName']
                        print (s3_response)
                        response = S3_CLIENT.put_bucket_acl(
                                ACL='public-read-write',
                                Bucket=m['S3BucketName']
                                )
                        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                            log.info('Resourse "' +varBucketName+ '" made non-compliant')
                    else:
                        varBucketName = m['S3BucketName']
                        log.info('Resourse "' +varBucketName+ '" is already non-compliant')

                elif varDecision is True:
                    if re.search(r'(global/AllUsers|global/AuthenticatedUsers)', str(s3_response)):
                        print(m['S3BucketName'])
                        varBucketName = m['S3BucketName']
                        print (s3_response)
                        response = S3_CLIENT.put_bucket_acl(
                                ACL='private',
                                Bucket=m['S3BucketName']
                                )
                        if response['ResponseMetadata']['HTTPStatusCode'] == 200:
                            log.info('Resourse "' +varBucketName+ '" made compliant')
                    else:
                        varBucketName = m['S3BucketName']
                        log.info('Resourse "' +varBucketName+ '" is already compliant')

#func_validate_compliant_or_not(True)

if func_user_input_validation() == 'compliantUpdate':
    log.info('The user request is to make resources compliant')
    log.info("Gathering information for non-compliant resources")
    func_validate_and_update(True)

elif func_user_input_validation() == 'nonCompliantUpdate':
    log.info('The user request is to make resources non-compliant')
    log.info("Gathering information for compliant resources")
    func_validate_and_update(False)

elif func_user_input_validation() == 'compliantDelete' or func_user_input_validation() == 'nonCompliantDelete' :   
    log.error("Deletion does not apply to this process.")

elif func_user_input_validation() == 'createcompliant' or func_user_input_validation() == "createnoncompliant":
    log.error("Creation does not apply to this process")
