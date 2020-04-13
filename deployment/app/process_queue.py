# Read messages from an SQS Queue (FIFO) and trigger the inferencing
import time
import sys
import boto3
import logging
import os
from urllib.parse import unquote

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/tmp/inference.log',
                    filemode='a')

sqs = boto3.resource('sqs')
# Get the queue
queue = sqs.get_queue_by_name(QueueName='gpt2-inference.fifo')

# Wait for run_time minutes before shutting down the instance to keep costs low
run_time = 15 # in minutes
timeout = time.time() + run_time*60
model_loaded_prefix = "/tmp/model-loaded-"

while time.time() < timeout:
    for message in queue.receive_messages(MessageAttributeNames=['model','prompt',"num_samples","batch_size","length","temperature","top_p","top_k"]):
        # Get the custom author message attribute if it was set        
        if message.message_attributes is not None:
            model = message.message_attributes.get('model').get('StringValue')
            prompt_url = message.message_attributes.get('prompt').get('StringValue')
            num_samples = message.message_attributes.get('num_samples').get('StringValue')
            batch_size = message.message_attributes.get('batch_size').get('StringValue')
            length = message.message_attributes.get('length').get('StringValue')
            temperature = message.message_attributes.get('temperature').get('StringValue')
            top_p = message.message_attributes.get('top_p').get('StringValue')
            top_k = message.message_attributes.get('top_k').get('StringValue')
            
            #print('Message {0} {1} {2} {3} {4} {5} {6} {7}'.format(model, prompt, num_samples, batch_size, length, temperature, top_p, top_k))
            timeout = time.time() + run_time*60
            cmd = "sudo shutdown -h +" + str(run_time)
            os.system(cmd)

            # Wait for a minute for model to be loaded if it is not still
            model_timeout = time.time() + 60   
            while not os.path.exists(model_loaded_prefix + model):
                time.sleep(1)
                if time.time() > model_timeout:
                    break

            port = 8081 if model == "left" else 8082
            cmd = f"curl --location --request GET 'http://127.0.0.1:{port}?prompt={prompt_url}&num_samples={num_samples}&batch_size={batch_size}&length={length}&temperature={temperature}&top_p={top_p}&top_k={top_k}' --header 'Content-Type: application/json'"
            
            # Replace %20 with ' '
            prompt = unquote(prompt_url)
            logging.info('process_queue: Generating text for [%s], model: [%s]', prompt, model)
            print(cmd)
            os.system(cmd)

            # Add all new prompts to a file which will be later updated to S3 for auto-completion..
            # Do it only for 1 model since prompt is same            
            if model == "left":
                with open("/home/ubuntu/new_prompts.txt", "a") as output:
                    output.write('%s\n' % prompt)

            try:
                # Let the queue know that the message is processed
                message.delete()
            except:
                logging.info("Got exception while calling message.delete()")

    #print(".", end= "")
    #sys.stdout.flush()
    time.sleep(1)

# Last run_time mins no messages received so shutdown the instance
cmd = "sudo shutdown -h now"
logging.info("Shutting down instance NOW")
os.system(cmd)
sys.exit()
