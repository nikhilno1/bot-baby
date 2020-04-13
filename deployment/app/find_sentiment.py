# Sample script to perform batch sentiment analysis using AWS Comprehend.

import boto3
import json

comprehend = boto3.client(service_name='comprehend', region_name='ap-south-1')
                
text = ["Sample 1", "Sample 2", "Sample 3"]

print('\n'.join('{}: {}'.format(*k) for k in enumerate(text)))

print('Calling DetectSentiment')
#print(json.dumps(comprehend.detect_sentiment(Text=text, LanguageCode='en'), sort_keys=True, indent=4))
result_list = comprehend.batch_detect_sentiment(TextList=text, LanguageCode='en')['ResultList']
max_score_list = []
top_sentiment_list = []
for result in result_list:    
    max_key = max(result['SentimentScore'], key=result['SentimentScore'].get)        
    max_score_list.append(result['SentimentScore'][max_key]) 
    top_sentiment_list.append(max_key)

max_score_list_s, top_sentiment_list_s, result_list_s = map(list, zip(*sorted(zip(max_score_list, top_sentiment_list, result_list), reverse=True)))

print("")
top_n_value = 5
print(max_score_list_s[0:top_n_value])
print(top_sentiment_list_s[0:top_n_value])
print(result_list_s[0:top_n_value])
print('End of DetectSentiment\n')
