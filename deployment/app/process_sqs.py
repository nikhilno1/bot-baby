import time
import sys
import boto3
import logging
import os

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/tmp/inference.log',
                    filemode='a')

sqs = boto3.resource('sqs')
# Get the queue
queue = sqs.get_queue_by_name(QueueName='gpt2-inference.fifo')

run_time = 10 # in minutes
timeout = time.time() + run_time*60   

while time.time() < timeout:
    for message in queue.receive_messages(MessageAttributeNames=['model','prompt',"num_samples","batch_size","length","temperature","top_p","top_k"]):
        # Get the custom author message attribute if it was set
        #print("message=",message.message_attributes)
        if message.message_attributes is not None:
            model = message.message_attributes.get('model').get('StringValue')
            prompt = message.message_attributes.get('prompt').get('StringValue')
            num_samples = message.message_attributes.get('num_samples').get('StringValue')
            batch_size = message.message_attributes.get('batch_size').get('StringValue')
            length = message.message_attributes.get('length').get('StringValue')
            temperature = message.message_attributes.get('temperature').get('StringValue')
            top_p = message.message_attributes.get('top_p').get('StringValue')
            top_k = message.message_attributes.get('top_k').get('StringValue')

        # Print out the body and author (if set)
        #print('Message {0} {1} {2} {3} {4} {5} {6} {7}'.format(model, prompt, num_samples, batch_size, length, temperature, top_p, top_k))
        timeout = time.time() + run_time*60
        cmd = "sudo shutdown -h +" + str(run_time)
        os.system(cmd)

        port = 8081 if model == "left" else 8082
        cmd = f"curl --location --request GET 'http://127.0.0.1:{port}?prompt={prompt}&num_samples={num_samples}&batch_size={batch_size}&length={length}&temperature={temperature}&top_p={top_p}&top_k={top_k}' --header 'Content-Type: application/json'"
        logging.info('Generating text for [%s], model: [%s]', prompt, model)
        print(cmd)
        os.system(cmd)

        # Let the queue know that the message is processed
        message.delete()

    print(".", end= "")
    sys.stdout.flush()
    time.sleep(1)

# Last run_time mins no messages received so shutdown the instance
cmd = "sudo shutdown -h now"
print("Shutting down instance NOW")
logging.info("Shutting down instance NOW")
os.system(cmd)

