import json, boto3, random, time
import urllib.parse
from boto3.dynamodb.conditions import Key
from collections import Counter
import ast

REGION = "ap-south-1"
INSTANCE_ID = 'i-0bd9ff717205bb43e' #AZ: ap-south-1b
#INSTANCE_ID = "i-02719d429a8908ae6" #AZ: ap-south-1c
ec2_client = boto3.client("ec2", region_name=REGION)
ec2_resource = boto3.resource("ec2", region_name=REGION)
dynamo_resource = boto3.resource('dynamodb', region_name=REGION)
ssm_client = boto3.client('ssm', region_name=REGION)
dynamodb = boto3.client('dynamodb')

# Create SQS client
sqs = boto3.client('sqs')
queue_url = 'https://sqs.ap-south-1.amazonaws.com/666268854852/gpt2-inference.fifo'

def send_sqs_message(msg_attr, msg_body):
    # Send message to SQS queue
    response = sqs.send_message(
        QueueUrl=queue_url,
        MessageGroupId="gpt2-inference",
        MessageAttributes=msg_attr,
        MessageBody=(msg_body)
    )
    
    print(response['MessageId'])

def execute_commands_on_linux_instances(client, commands, instance_ids):
    """Runs commands on remote linux instances
    :param client: a boto/boto3 ssm client
    :param commands: a list of strings, each one a command to execute on the instances
    :param instance_ids: a list of instance_id strings, of the instances on which to execute the command
    :return: the response from the send_command function (check the boto3 docs for ssm client.send_command() )
    """

    resp = client.send_command(
        DocumentName="AWS-RunShellScript", # One of AWS' preconfigured documents
        Parameters={'commands': commands},
        InstanceIds=instance_ids,
    )
    return resp

def get_majority_view(text, sentiment):
    c = Counter(sentiment)
    value, count = c.most_common()[0]
    #print(value, count)

    text_m = []
    sentiment_m = []
    for t, s in zip(text, sentiment):
        if s == value:
            text_m.append(t)
            sentiment_m.append(s)
    #print(text_m)
    #print(sentiment_m)
    return text_m, sentiment_m

def format_response(resp, status_code):
    if status_code == 200:
        # Return the majority view of the tweets
        text_l, sentiment_l = get_majority_view(ast.literal_eval(resp['text']), ast.literal_eval(resp['sentiment']))
        message = [{"text": t, "sentiment": s} for t, s in zip(text_l, sentiment_l)]
    else:
        message = resp
    return {
        "statusCode": str(status_code),
        "body": json.dumps(message),
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
        },
    }

def truncate_to_n_words(s, n):
    return ' '.join(s.split()[:n])
    
def lambda_handler(event, context):
    
    print('## EVENT')
    #print(event)
    
    model = event["queryStringParameters"]["model"].strip()
    if model != "left" and model != "right":
        model = "left"
    
    prompt = event["queryStringParameters"]["prompt"].strip()
    print("prompt: %s, model: %s" % (prompt, model))
    prompt = truncate_to_n_words(prompt, 20)
    if prompt is None:
        prompt = "The"
    prompt_lcase = prompt.lower()
    
    # Check if the prompt is already present in the DynamodDB
    table = dynamo_resource.Table('gpt2-tweets-' + model)
    timeout = time.time() + 10   # 10 second from now
    while True:
        resp = table.query(KeyConditionExpression=Key('prompt').eq(prompt_lcase))
        if len(resp['Items'])>0 or time.time() > timeout:
            break
        time.sleep(1)
    
    if len(resp['Items'])>0:
        print("The query returned the following existing items:")
        print(resp['Items'])
        #Increment the visits counter        
        dynamodb.update_item(
            TableName='gpt2-tweets-' + model, 
            Key={
                'prompt':{'S': prompt_lcase}
            },
            UpdateExpression='SET visits = visits + :inc',
            ExpressionAttributeValues={
                ':inc': {'N': '1'}
            },
            ReturnValues="NONE"
        )
        return format_response(resp['Items'][0], 200)
    
    
    # Add a space at the end to end the prompt on whole words
    prompt_url = urllib.parse.quote(prompt) 
    port = 8081 if model == "left" else 8082
    
    #samples = int(event["queryStringParameters"]["num_samples"])
    samples = 20
    
    #words = int(event["queryStringParameters"]["length"])
    words = 60
    
    #temperature = float(event["queryStringParameters"]["temperature"])
    temperature = 0.7
    
    #nucleus = float(event["queryStringParameters"]["top_p"])
    nucleus = 0.9
    
    #topn = int(event["queryStringParameters"]["top_k"])
    topn = 40
    
    batch_size = 20
    
    msg_attr = {
                    'model': {
                        'DataType': 'String',
                        'StringValue': model
                    },
                    'prompt': {
                        'DataType': 'String',
                        'StringValue': prompt_url
                    },
                    'num_samples': {
                        'DataType': 'Number',
                        'StringValue': str(samples)
                    },
                    'batch_size': {
                        'DataType': 'Number',
                        'StringValue': str(batch_size)
                    },
                    'length': {
                        'DataType': 'Number',
                        'StringValue': str(words)
                    },
                    'temperature': {
                        'DataType': 'Number',
                        'StringValue': str(temperature)
                    },
                    'top_p': {
                        'DataType': 'Number',
                        'StringValue': str(nucleus)
                    },
                    'top_k': {
                        'DataType': 'Number',
                        'StringValue': str(topn)
                    }
                }
    # Add a random number to get around queue de-deplication
    #rand_num = random.randint(1, 1000000)
    rand_num = 7
    msg_body = "Model = " + model + ",Prompt = " + prompt_url + ",rand = " + str(rand_num)
    send_sqs_message(msg_attr, msg_body)
    
    # If not, then run the inference, add to DB and return
    status = ec2_client.describe_instance_status(InstanceIds=[INSTANCE_ID])
    if len(status['InstanceStatuses']) == 0: ec2_client.start_instances(InstanceIds=[INSTANCE_ID])        
    
    instance = ec2_resource.Instance(INSTANCE_ID)
    instance.wait_until_running()
    waiter = ec2_client.get_waiter('instance_status_ok')
    waiter.wait(InstanceIds=[INSTANCE_ID])
    
    #dynamoid = random.randint(1, 1000000)
    
    commands = ["cd /home/ubuntu",
                "shutdown -h +15"]
                #"sudo -i -u ubuntu bash <<-EOF",
                #"source ~/.bashrc",
                #"source env/bin/activate",
                #f"curl --location --request GET 'http://127.0.0.1:{port}?prompt={prompt_url}&num_samples={samples}&batch_size={batch_size}&length={words}&temperature={temperature}&top_p={nucleus}&top_k={topn}' --header 'Content-Type: application/json'"]
                #f"python3 gpt2-script.py --model=\"{model}\" --prompt=\"{prompt}\" --num_samples={samples} --batch_size={batch_size} --length={words} --temperature={temperature} --top_p={nucleus} --top_k={topn}"]
    
    print(commands)
    execute_commands_on_linux_instances(ssm_client, commands, [INSTANCE_ID])
    
    timeout = time.time() + 60*2   # 2 minutes from now
    while True:
        resp = table.query(KeyConditionExpression=Key('prompt').eq(prompt_lcase))
        if len(resp['Items'])>0 or time.time() > timeout:
            break
        time.sleep(1)
    
    print("The query returned the following items:")
    print(resp['Items'])
    
    return format_response(resp['Items'][0], 200)