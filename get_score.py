import httplib, urllib, base64
import boto3
import botocore
import os
import json
import io
import requests
import threading
import time

def score_handler(event, context):
    download_score()
    scores_json = calculate_score()
    print scores_json
    return scores_json

def download_score():
    access_key = os.environ['KEY']
    secret_access_key = os.environ['SECRET_KEY']
    BUCKET_NAME = 'newscorebucket'
    s3 = boto3.resource('s3',region_name='us-east-1',aws_access_key_id=access_key,
         aws_secret_access_key=secret_access_key)
    try:
        s3.Bucket(BUCKET_NAME).download_file('score', '/tmp/score')
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise

def calculate_score():
    filename = '/tmp/score'
    score_dict = dict()
    with open(filename, 'r') as f:
        list1 = f.readlines()
    print list1
    print '***************'
    final_str = ' '

    for i in range(len(list1)):
        score_dict = dict()
        line = list1[i] 
        ele = line.strip()
        image_number = ele.split(',')[0]
        image_score = ele.split(',')[1]
        score_dict[image_number] = image_score
        temp_str = json.dumps(score_dict)
        final_str = final_str[:-1] + ',' + temp_str[1:]
    final_str = '{' + final_str[1:]
    return final_str




#
if __name__ == "__main__":
    # download_score()
    print (calculate_score())
