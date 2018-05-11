import boto3
from termcolor import colored
import requests
import time
import random

# Get config
with open('andrewid.txt','r') as f:
    lines = f.readlines()
    andrewid = lines[0][:-1]
    password = lines[1]

with open('aws.txt','r') as f:
    lines = f.readlines()
    aws_id = lines[0].strip()
    aws_password = lines[1]
    
# Connection
ec2 = boto3.resource('ec2',region_name='us-east-1',aws_access_key_id=aws_id,
         aws_secret_access_key=aws_password)

# Production-Create load generator
# Step 1


ec2.create_instances(ImageId='ami-7747a30d',InstanceType='m3.medium',MinCount=1, MaxCount=1,
                     SecurityGroups=['default',],SecurityGroupIds=['default',],
                     KeyName='15319demo',
                     TagSpecifications=[{'ResourceType': 'instance',
                        'Tags': [{'Key':'Project','Value':'2.1'}]}])
time_start = time.time()
time_create_ws = time.time()

# Step 3
# Submit password and andrewid to the load generator
load_gen_is_ready = 0
while (load_gen_is_ready == 0):
    try:
        for i in ec2.instances.all():
            if i.image_id == 'ami-7747a30d' and len(i.public_dns_name)> 10:
                load_generator_dns = i.public_dns_name
                url_load_gen = 'http://'+i.public_dns_name+'/password?passwd='+password+'&andrewid='+andrewid
                print (url_load_gen)
                break
        result_load_gen = requests.get(url_load_gen)
        load_gen_is_ready = 1
        print ('Load generator is ready!')
        time_end = time.time()
        print('It has taken {0} sec to prepare load generator'.format(time_end - time_start))
    except:
        time.sleep(5)

# Production-Create web service
# Step 2 
present_rps = 0
url_sub_gen_list = []
test_start = 0
while (present_rps < 4000):
    if(time.time() - time_start < 100 or time.time() - time_create_ws < 100):
        time.sleep(max(1,101- (time.time() - time_create_ws)))
    ec2.create_instances(ImageId='ami-247a9e5e',InstanceType='m3.medium',MinCount=1, MaxCount=1,
                         SecurityGroups=['default',],SecurityGroupIds=['default',],
                         KeyName='15319demo',
                         TagSpecifications=[{'ResourceType': 'instance',
                            'Tags': [{'Key':'Project','Value':'2.1'}]}])
    time_create_ws = time.time()

    # Step 5 & 6
    # Submit the web service VM's DNS name to the load generator to start the test or to add up web service
    url_sub_gen_is_ready = 0
    while (url_sub_gen_is_ready == 0):
        try:
            # Step 4 
            # Check if the test is not start
            for i in ec2.instances.all():
                web_service_instance_dns = i.public_dns_name
                if i.image_id == 'ami-247a9e5e' and len(web_service_instance_dns)> 10 and i.public_dns_name not in url_sub_gen_list:
                    if test_start == 0:
                        url_sub_gen = 'http://'+load_generator_dns+'/test/horizontal?dns='+web_service_instance_dns
                        test_start = 1
                        time_end = time.time()
                        print ('It has passed {0} seconds! to add the 1st web service'.format(time_end - time_start))
                        url_sub_gen_list.append(i.public_dns_name)
                    else:
                        url_sub_gen = 'http://'+load_generator_dns+'/test/horizontal/add?dns='+web_service_instance_dns
                        time_end = time.time()
                        print ('It has passed {0} seconds! to add {1} web service!'.format(time_end - time_start, len(url_sub_gen_list)))
                        url_sub_gen_list.append(i.public_dns_name)
                    print ('url_sub_gen is: ',url_sub_gen)
            
            result_sub_gen = requests.get(url_sub_gen)
            # log might not ready
            try:
                test_number = result_sub_gen.text.split('/log?name=test.')[1].split('.log')[0]
                url_rps = 'http://'+load_generator_dns+'/log?name=test.'+test_number+'.log'
                print(len(url_sub_gen_list),test_number)
                print(url_rps)
                result_log = requests.get(url_rps)
                temp_list = result_log.text.split('\n')
                for i in range(1,len(temp_list)):
                    if temp_list[-i].find('Current rps=') != -1:
                        present_rps = float(temp_list[-i].replace('Current rps=','').replace('[','').replace(']',''))
                        print ('present_rps is: ', present_rps)
                        break
                url_sub_gen_is_ready = 1
            except Exception as e:
                pass
        except Exception as e:
            print(e)
            time.sleep(5)
    time_end = time.time()
    print ('Sucessfully installed {0} web service in the {1} sec'.format(len(url_sub_gen_list), time_end - time_start))
    