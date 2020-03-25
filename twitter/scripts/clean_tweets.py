# Remove URL
import re

with open("../temp/all_tweets.txt") as f:
    all_tweets = [line.rstrip() for line in f]    
    
    with open("../temp/all_tweets_cleaned.txt", 'w',encoding="utf-8") as output:
        for tweet in all_tweets:
            #tweet = re.sub(r'http\S+', '', tweet, flags=re.MULTILINE)
            tweet = re.sub(r"(?:\@|https?\://)\S+", "", tweet, flags=re.MULTILINE)
            tweet = re.sub("([^\x00-\x7F])+"," ",tweet)
            tweet = ' '.join(tweet.split())
            tweet = tweet.replace('&amp;', '&')
            #return re.sub(r"http\S+", "", sample)
            if len(tweet) > 50:
                output.write('%s\n' % tweet)

            
