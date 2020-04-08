from __future__ import absolute_import, division, print_function, unicode_literals

import logging
from starlette.applications import Starlette
from starlette.responses import UJSONResponse
import json
import gpt_2_simple as gpt2
import tensorflow as tf
import uvicorn
import os
import gc
import sys
import boto3
import nltk
from nltk.tokenize import sent_tokenize
from pathlib import Path
from urllib.parse import unquote
from datetime import datetime
import decimal

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if abs(o) % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

app = Starlette(debug=False)

script_path = os.path.dirname(os.path.abspath( __file__ ))

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s',
                    filename='/tmp/inference.log',
                    filemode='a')

logging.info('Starting gpt2 session')

model = os.environ.get('MODEL', 'left')
print("Got model = " + model)
checkpoint_path = script_path + "/model/" + model+ "/checkpoint/"
sess = gpt2.start_tf_sess(threads=1)
gpt2.load_gpt2(sess, checkpoint_dir=checkpoint_path)

# Touch the file which the process_sqs waits on
Path('/tmp/model-loaded-'+model).touch()

# Needed to avoid cross-domain issues
response_header = {
    'Access-Control-Allow-Origin': '*'
}

generate_count = 0

def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]

def get_sentiment(all_tweets):
    comprehend = boto3.client(service_name='comprehend', region_name='ap-south-1')
    result_list = comprehend.batch_detect_sentiment(TextList=all_tweets, LanguageCode='en')['ResultList']
    max_score_list = []
    top_sentiment_list = []
    for result in result_list:
        max_key = max(result['SentimentScore'], key=result['SentimentScore'].get)
        #print(result)
        #print(result['SentimentScore'][max_key])
        max_score_list.append(result['SentimentScore'][max_key])
        top_sentiment_list.append(max_key)
    #print(max_score_list)
    #print(top_sentiment_list)
    #print(json.dumps(result, indent=4))
    # First sort based on score, keep the top N (for eg. 5), then sort again based on sentiment
    max_s, senti_s, tweets_s = map(list, zip(*sorted(zip(max_score_list, top_sentiment_list, all_tweets), reverse=True)))
    top_sentiment_list_s, max_score_list_s, tweets_list_s = map(list, zip(*sorted(zip(senti_s[:10], max_s[:10], tweets_s[:10]), reverse=True)))
    return tweets_list_s, top_sentiment_list_s, max_score_list_s

@app.route('/', methods=['GET', 'POST', 'HEAD'])
async def homepage(request):
    global generate_count
    global sess
    global script_path

    if request.method == 'GET':
        params = request.query_params
    elif request.method == 'POST':
        params = await request.json()
    elif request.method == 'HEAD':
        return UJSONResponse({'text': ''},
                             headers=response_header)

    #prompt=params.get('prompt', '')[:100]
    prompt=(params.get('prompt', ''))
    if prompt is None:
        prompt = "<|startoftext|>"
    logging.info('Generating text for [%s], model: [%s]', prompt, model)

    unproc_tweets_list = gpt2.generate(sess, checkpoint_dir=checkpoint_path,
                             length=int(params.get('length', 80)),
                             nsamples=int(params.get('num_samples', 20)),
                             temperature=float(params.get('temperature', 0.7)),
                             top_k=int(params.get('top_k', 40)),
                             top_p=float(params.get('top_p', 0.9)),
                             prefix=prompt,
                             truncate=params.get('truncate', "<|endoftext|>"),
                             include_prefix=str(params.get(
                                 'include_prefix', True)).lower() == 'true',
                             batch_size=int(params.get('batch_size', 20)),
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
        t = ' '.join(unique(t_list))

        # Some tweets have repeated words. Remove the ones below a threshold. 
        if len(set(t.split())) > 20:
            proc_tweets_list.append(t)
        else:
            deleted_list.append(t)

    #logging.info("======2=======")
    #logging.info(proc_tweets_list)
    #logging.info("======3=======")
    #logging.info(deleted_list)
    #logging.info("==============")
    logging.info("Generated %d tweets", len(proc_tweets_list))

    if len(proc_tweets_list) > 0:
        # Find the sentiment of the tweets using AWS comprehend 
        tweets_list, sentiment_list, score_list = get_sentiment(proc_tweets_list)

        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        table = dynamodb.Table('gpt2-tweets-' + model)
        json_text = json.dumps(tweets_list)
        json_sentiment = json.dumps(sentiment_list)
        json_score = json.dumps(score_list)
        timestamp = datetime.now().isoformat()
        logging.info('Adding to DynamoDB DB, prompt: [%s], model: %s', prompt.lower(), model)
        print
        table.put_item(
            Item={
                'prompt' : prompt.lower(),
                'text' : json_text,
                'orig_prompt' : prompt,
                'sentiment' : json_sentiment,
                'score' : json_score,
                'timestamp': timestamp,
                'visits': decimal.Decimal(1)
            }
        )
        # Add all new prompts to a file for auto-completion..but only for 1 model
        if model == "left":
            with open("/home/ubuntu/new_prompts.txt", "a") as output:
                output.write('%s\n' % prompt)

    logging.info('Finished executing script')

#    generate_count += 1
#    if generate_count == 8:
#        # Reload model to prevent Graph/Session from going OOM
#        tf.reset_default_graph()
#        sess.close()
#        sess = gpt2.start_tf_sess(threads=1)
#        gpt2.load_gpt2(sess)
#        generate_count = 0
#
#    gc.collect()
    return UJSONResponse({'text': proc_tweets_list}, headers=response_header)

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=int(os.environ.get('PORT', 8080)))
