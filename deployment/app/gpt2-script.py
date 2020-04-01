from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import socket
import time
import logging
import argparse
import json
import gpt_2_simple as gpt2
import tensorflow as tf
import boto3
import nltk
from nltk.tokenize import sent_tokenize

def get_lock(process_name):
    # Without holding a reference to our socket somewhere it gets garbage
    # collected when the function exits
    get_lock._lock_socket = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    try:
        # The null byte (\0) means the the socket is created 
        # in the abstract namespace instead of being created 
        # on the file system itself.
        # Works only in Linux
        get_lock._lock_socket.bind('\0' + process_name)
        print('I got the lock')
        return True
    except socket.error:
        print('lock exists')
        return False

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=str, default="left")
    parser.add_argument("--prompt", type=str, default=" ")
    parser.add_argument("--truncate", type=str, default="<|endoftext|>")
    parser.add_argument("--include_prefix", type=str, default=False)
    parser.add_argument("--length", type=int, default=60)
    parser.add_argument("--num_samples", type=int, default=3)
    parser.add_argument("--batch_size", type=int, default=3)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--top_k", type=int, default=0)
    parser.add_argument("--top_p", type=float, default=0.9)
    args = parser.parse_args()
       
    logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/tmp/inference.log',
                    filemode='a')

    pid = str(os.getpid())
    loop = 0
    while get_lock('gpt2-script') is False and loop < 120:
        if loop % 30 == 0:
            logging.info('[%s]: Another instance found running. Sleeping', pid)
        time.sleep(1)
        loop += 1

    if loop == 120:
        logging.info('[%s]: Found instance running for 2 mins. Exiting.', pid)
        sys.exit()

    logging.info('[%s]: Starting gpt2 session', pid)
    checkpoint_dir = "./model/" + args.model + "/checkpoint"
    print("Checkpoint dir: %s" % checkpoint_dir)
    sess = gpt2.start_tf_sess(threads=1)
    gpt2.load_gpt2(sess, checkpoint_dir=checkpoint_dir)

    #prompt=args.prompt[:100]
    prompt=args.prompt
    if prompt is " ":
        prompt = "<|startoftext|>"

    logging.info('[%s]: Generating text for [%s], model: [%s]', pid, prompt, args.model)

    unproc_tweets_list = gpt2.generate(sess,
                            checkpoint_dir=checkpoint_dir,
                            length=args.length,
                            nsamples=args.num_samples,
                            temperature=args.temperature,
                            top_k=args.top_k,
                            top_p=args.top_p,
                            prefix=prompt,
                            truncate=args.truncate,
                            include_prefix=str(args.include_prefix).lower() == 'true',
                            batch_size=args.batch_size,
                            return_as_list=True
                         )

    proc_tweets_list = []
    deleted_list = []

    for raw_tweet in unproc_tweets_list:
        # Remove \n and " characters
        t=raw_tweet.replace('\n',' ')
        t=t.replace('\"','')

        # Break the text into sentences and remove the last sentence which is most likely to be incomplete
        t_list = sent_tokenize(t)
        del t_list[-1]
        t = ' '.join(t_list)


        # Some tweets have repeated words. Remove the ones below a threshold. 
        if len(set(t.split())) > 20:
            proc_tweets_list.append(t)
        else:
            deleted_list.append(t)

    print("======1======")
    print(proc_tweets_list)
    print("======2======")
    print(deleted_list)

    if len(proc_tweets_list) > 0:
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        table = dynamodb.Table('gpt2-tweets-' + args.model)
        json_text = json.dumps(proc_tweets_list)
        logging.info('[%s]: Adding to DynamoDB, prompt: [%s], model: [%s]', pid, args.prompt.lower(), args.model)
        print
        table.put_item(
            Item={
                'prompt' : args.prompt.lower(),
                'text' : json_text
            }
        )
        logging.info('[%s]: Finished executing script', pid)

if __name__ == '__main__':
    main()

