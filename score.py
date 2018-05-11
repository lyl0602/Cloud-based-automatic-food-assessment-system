import httplib, urllib, base64
import boto3
import botocore
import os
import json
import io
import requests
import threading
import time
import sys




search_dict={'coke':'-1', 'soda': '-1','dessert':'-1','roasting':'-1','cheese':'-1','flatbread':'-1','pie':'-1','roast':'-1','fries':'-1','dog':'-1','fries':'-1','chocolate':'-1','sugar':'-1',
'junk':'-1','fast':'-1','hamburger':'-1','fried':'-1','bbq':'-1','cake':'-1','butter':'-1','creme':'-1','pita':'-1','burger':'-1','nuggets':'-1','nachos':'-1',
'donut':'-1','bacon':'-1','cupcake':'-1','cream':'-1','sweets':'-1','candy':'-1','pizza':'-1','cheeseburger':'-1','confectionerywa':'-1','waffle':'-1','pastry':'-1',
'sprinkles':'-1','cookies':'-1','snack':'-1','pancake':'-1','custard':'-1','fudge':'-1','brownie':'-1','loaf':'-1','biscuit':'-1','cracker':'-1','pretzel':'-1','prosciutto':'-1',
'ham':'-1','bayonne':'-1','asian':'0','american':'-1','grill':'-1','sausage':'-1','patty':'-1','barbecue':'-1','grillades':'-1','grilling':'0','naporitan':'0','bucatini':'0',
'sandwich':'0','taco':'0','burrito':'0','vermicelli':'0','perciatelli':'0','noodle':'0','toast':'0','wrap':'0','raviolli':'0','steak':'0','beef':'0','ribs':'0',
'pork':'0','pasta':'0','macaroni':'0','spaghetti':'0','penne':'0','tortellini':'0','bread':'0','meatball':'0','chop':'0','brisket':'0','bogoli':'0','soup':'0',
'strawberries':'1','superfood':'1','lettuce':'1','homarus':'1','natural':'1','peach':'1','rotisserie':'1','fattoush':'1','leaf':'1','fish':'1','vegeterian':'1','salmon':'1',
'kiwifruit':'1','vegetarian':'1','pomegranate':'1','spinach':'1','seashell':'1','broccoli':'1','clam':'1','oyster':'1','herring':'1','sardine':'1','lime':'1',
'grapefruit':'1','':'1','lemon':'1','crab':'1','raspberry':'1','strawberry':'1','radish':'1','cabbage':'1','turnip':'1','agaric':'1','mushroom':'1',
'potato':'1','juice':'1','arugula':'1','lobster':'1','avocado':'1','cherry':'1','shrimp':'1','carrot':'1','persimmon':'1','pomelo':'1','citrus':'1','kiwi':'1','cauliflower':'1',
'sushi':'1','watermelon':'1','seafood':'1','vegetable':'1','apple':'1','orange':'1','grapes':'1','fruit':'1','salad':'1','banana':'1','mango':'1','olive':'1',
'pear':'1', 'coconut':'1','pineapple':'1','cucumber':'1','tomato':'1','drug':'-10','cigarette':'-3','pill':'-10','medicine':'-10','alcohol':'-3','beer':'-3','wine':'-3',
'exercise':'5','sports':'5','gym':'5','venue':'5','training':'5','fitness':'5','dumbbell':'5','barbell':'5'}



class AzureThread (threading.Thread):
   def __init__(self, image_url):
    threading.Thread.__init__(self)
    self.image_url = image_url
    self.score = 0
   def run(self):
    azure_result = get_azure_result(self.image_url)
    azure_tags = parse_azure_result(azure_result)
    self.score = calculate_score(azure_tags, search_dict)
    print ('Azure Score' + str(self.score))
    print azure_tags


class AwsThread (threading.Thread):
   def __init__(self, image_url):
    threading.Thread.__init__(self)
    self.image_url = image_url
    self.score = 0
   def run(self):
    aws_result = get_aws_result(self.image_url)
    aws_tags = parse_aws_result(aws_result)
    self.score = calculate_score(aws_tags, search_dict)
    print ('Aws Score' + str(self.score))
    print aws_tags


class GcpThread (threading.Thread):
   def __init__(self, image_url):
    threading.Thread.__init__(self)
    self.image_url = image_url
    self.score = 0
   def run(self):
    gcp_result = get_gcp_result(self.image_url)
    gcp_tags = parse_gcp_result(gcp_result)
    self.score = calculate_score(gcp_tags, search_dict)
    print gcp_tags
    print ('The gcp score of picture is' + str(self.score))
    print (image_url)



def score_handler(event, context):

    bucket= event['queryStringParameters']['bucket']

    # Delete all the files in receive bucket, initialize
    receive_bucket = 'josienewbucket'
    s3 = boto3.resource('s3')
    s3.Bucket(receive_bucket).objects.all().delete()

    if (bucket != receive_bucket ):
        copy_bucket(bucket, receive_bucket)

    file_ls = show_bucket_filename(receive_bucket)
    score_ls = []
    # file_number = 0
    file_ls


    for file_name in file_ls:
        api_score_list = [0.0] * 3
        image_url = 'https://s3.amazonaws.com/'+ receive_bucket +'/' + file_name
        print file_name

        # Use multi-thread function to speed up
        # We ain't ever getting older
        azureThread = AzureThread(image_url)
        gcpThread = GcpThread(image_url)
        awsThread = AwsThread(image_url)

        azureThread.start()
        gcpThread.start()
        awsThread.start()

        azureThread.join()
        gcpThread.join()
        awsThread.join()

        api_score_list = [azureThread.score, gcpThread.score, awsThread.score]

        score = calculate_final_score(api_score_list)


        score_ls.append(score)

    save_score(score_ls)
    upload_score()

    return {"statusCode": 200, \
        "headers": {"Content-Type": "application/json"}, \
        "body" :  bucket}


def get_gcp_result(img_url):
    GCP_KEY = os.environ['GCP_KEY']
    headers = {
        'Content-Type': 'application/json'
    }

    body = {
        "requests": [
            {
              "image": {
                "source": {
                  "imageUri": img_url
                }
              },
              "features": [
                {
                  "type": "LABEL_DETECTION"
                }
              ]
            }
          ]
          }

    response = requests.post('https://vision.googleapis.com/v1/images:annotate?key=' + GCP_KEY, data=json.dumps(body), headers=headers)
    return response.json()

def get_aws_result(img_url):
    try:
        for i in range(len(img_url)):
            if img_url[i] == '/':
                n = i

        file_name = img_url[n+1:]
        bucket_http = img_url[:n]
        for i in range(len(bucket_http)):
            if bucket_http[i] == '/':
                n = i
        bucket = bucket_http[n+1:]

        access_key = os.environ['KEY']
        secret_access_key = os.environ['SECRET_KEY']
        client=boto3.client('rekognition',region_name='us-east-1',aws_access_key_id=access_key,
             aws_secret_access_key=secret_access_key)
        response = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':file_name}})
        return response
    except:
        print 'AWS result Failed to get'
        print img_url

def get_azure_result(img_url):
    uri_base = 'eastus.api.cognitive.microsoft.com'
    subscription_key = os.environ['AZURE_KEY']
    headers = {
        # Request headers.
        'Content-Type': 'application/json',
        'Ocp-Apim-Subscription-Key': subscription_key,
    }

    params = urllib.urlencode({
        # Request parameters. All of them are optional.
        'visualFeatures': 'Categories,Description,Color',
        'language': 'en',
    })

    # The URL of a JPEG image to analyze.
    body = "{'url': \'" + img_url + '\'}'

    try:
        # Execute the REST API call and get the response.
        conn = httplib.HTTPSConnection('westcentralus.api.cognitive.microsoft.com')
        conn.request("POST", "/vision/v1.0/tag?%s" % params, body, headers)
        response = conn.getresponse()
        data = response.read()

        # 'data' contains the JSON data. The following formats the JSON data for display.
        parsed = json.loads(data)
        conn.close()
        return parsed

    except Exception as e:
        print('Error:')
        print(e)
        return None

def parse_gcp_result(res):
    if type(res) == 'str':
	res = json.loads(res)
    print ("GCP OUTPUT:")
    tmp_dict = res['responses'][0]
    if type(tmp_dict) == 'str':
        tmp_dict = json.loads(tmp_dict)
    descr_list = tmp_dict['labelAnnotations']
    final_list = []
    for descr in descr_list:
    	description = descr['description']
	   score = float(descr['score'])
	   if score >= 0.6:
    	   final_list.append(description)
    print final_list
    return final_list

def parse_azure_result(res):
    if type(res) == 'str':
       res = json.loads(res)
    if 'tags' in res:
        descr_list = res['tags']
        final_list = []
        for descr in descr_list:
            description = descr['name']
            final_list.append(description)
        print 'Azure:'
        print final_list

        return final_list
    else:
        print ('Azure result is wrong, the res is:')
        print (res)
        return None

def parse_aws_result(res):
    if type(res) == 'str':
        res = json.loads(res)
    descr_list = res['Labels']
    final_list = []
    for descr in descr_list:
        description = descr['Name']
        final_list.append(description)
    print final_list
    return final_list

# Calculate score by labels of one pic
def calculate_score(li, search_dict):
    li_split = []
    di_split = {}
    health_score = 0.0
    unhealth_score = 0.0
    score = 0.0

    for label in li:
        li_split += label.split(' ')

    li_split_new = []
    for ele in li_split:
        li_split_new.append(ele.lower())


    for label in li_split_new:
        if search_dict.has_key(label):
            score = float(search_dict[label])
            if (score > 0):
                health_score = score
            elif (score < 0):
                unhealth_score = score


    return health_score + unhealth_score


def calculate_final_score(api_score_list):
    score = api_score_list[0] * 0.1 + api_score_list[1] * 0.8 + api_score_list[2] * 0.1
    return score

def save_score(li):
    filename = '/tmp/score'
    with open(filename,'w') as f:
        pass
    for image_number in range(len(li)):
        append_write = 'a'
        value = li[image_number]
        print image_number,value
        value = 2.0*(image_number+1)*value/(len(li)+1)
        print value
        with open(filename,append_write) as f:
            print str(image_number+1) + ',' + str(value)+'\n'
            f.write(str(image_number+1) + ',' + str(value)+'\n')
            

def upload_score():
    access_key = os.environ['KEY']
    secret_access_key = os.environ['SECRET_KEY']
    s3 = boto3.resource('s3',region_name='us-east-1',aws_access_key_id=access_key,
         aws_secret_access_key=secret_access_key)

    data = open('/tmp/score', 'rb')
    s3.Bucket('newscorebucket').put_object(Key='score', Body=data)
    # s3.Bucket('15319imagebucket3').put_object(Key='score', Body=data)

def show_bucket_filename(bucket_name):
    filename_list = []
    s3client = boto3.client('s3')

    try:
        obj_list = s3client.list_objects(Bucket=bucket_name)['Contents']
        print obj_list
        for key in obj_list:
            filename_list.append(key['Key'])

        return (filename_list)
    except Exception as e:
        print e
        return None

def copy_bucket(source_bucket, dest_bucket):
    s3resource = boto3.resource('s3')
    filename_list = show_bucket_filename(source_bucket)
        print "The source bucket has:"
        print filename_list
    print "The destination bucket has:"
        print show_bucket_filename(dest_bucket)
    for filename in filename_list:
        copy_source = {'Bucket': source_bucket, 'Key': filename}
        s3resource.meta.client.copy(copy_source, dest_bucket,filename)
    print show_bucket_filename(dest_bucket)



if __name__ == "__main__":
    bucket = sys.argv[1]
    receive_bucket = 'josienewbucket'

    # Delete all the files in bucket
    s3 = boto3.resource('s3')
    s3.Bucket(receive_bucket).objects.all().delete()

    if (bucket != receive_bucket):
        copy_bucket(bucket, receive_bucket)

    score_ls = []
    file_ls = show_bucket_filename(receive_bucket)
    file_ls.sort()
    print ('Going to check these foods:')
    print (file_ls)

    for file_name in file_ls:
        image_url = 'https://s3.amazonaws.com/'+receive_bucket+ '/' + file_name

        azureThread = AzureThread(image_url)
        gcpThread = GcpThread(image_url)
        awsThread = AwsThread(image_url)

        azureThread.start()
        gcpThread.start()
        awsThread.start()

        azureThread.join()
        gcpThread.join()
        awsThread.join()

        api_score_list = [azureThread.score, gcpThread.score, awsThread.score]

        score = calculate_final_score(api_score_list)


        score_ls.append(score)
        print file_name, score
    print (score_ls)

    save_score(score_ls)
    upload_score()
