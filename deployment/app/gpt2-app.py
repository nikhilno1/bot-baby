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

# Needed to avoid cross-domain issues
response_header = {
    'Access-Control-Allow-Origin': '*'
}

generate_count = 0

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
    prompt=params.get('prompt', '')
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
        t = ' '.join(t_list)

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
        dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
        table = dynamodb.Table('gpt2-tweets-' + model)
        json_text = json.dumps(proc_tweets_list)
        logging.info('Adding to DynamoDB DB, prompt: [%s], model: %s', prompt.lower(), model)
        print
        table.put_item(
            Item={
                'prompt' : prompt.lower(),
                'text' : json_text
            }
        )
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

