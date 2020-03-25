from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import argparse
import json
import gpt_2_simple as gpt2
import tensorflow as tf
import boto3
import nltk
from nltk.tokenize import sent_tokenize


def main():
    parser = argparse.ArgumentParser()
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

    logging.info('Starting gpt2 session')

    sess = gpt2.start_tf_sess(threads=1)
    gpt2.load_gpt2(sess)

    prompt=args.prompt[:20]
    if prompt is " ":
        prompt = "<|startoftext|>"

    logging.info('Generating text for [%s]', prompt)

    unproc_tweets_list = gpt2.generate(sess,
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
        table = dynamodb.Table('gpt2-tweets-right')
        json_text = json.dumps(proc_tweets_list)
        logging.info('Adding to DynamoDB ID: %s, tweet: %s', args.prompt, json_text)
        print
        table.put_item(
            Item={
                'prompt' : args.prompt,
                'text' : json_text
            }
        )
    logging.info('Finished executing script')

if __name__ == '__main__':
    main()

