# Imports
import GetOldTweets3 as got
import pandas as pd
import time

# Function the pulls tweets from a specific username and turns to csv file

# Parameters: (list of twitter usernames), (max number of most recent tweets to pull from)
def username_tweets_to_csv(username, count):
    # Creation of query object
    tweetCriteria = got.manager.TweetCriteria().setUsername(username)\
                                            .setSince("2014-01-01")\
                                            .setMaxTweets(count)\
                                            .setEmoji("unicode")
    try:                                            
        # Creation of list that contains all tweets
        tweets = got.manager.TweetManager.getTweets(tweetCriteria)
        # Creating list of chosen tweet data
        user_tweets = [[tweet.date, tweet.text] for tweet in tweets]

        # Creation of dataframe from tweets list
        tweets_df = pd.DataFrame(user_tweets, columns = ['Datetime', 'Text'])

        # Converting dataframe to CSV
        tweets_df.to_csv('../data/right/tweets/original/{}-{}k-tweets.csv'.format(username, int(count/1000)), sep=',')

    except: 
        print("Caught Exception. Sleeping...")
        time.sleep(200)

print("Reading followers")
with open("../data/right/all_followers_username.txt") as f:
    user_list = [line.rstrip() for line in f]

with open("../data/right/tweets/fetched_list.txt") as f:
    fetched_list = [line.rstrip() for line in f]

with open("../data/right/tweets/fetched_list.txt", "a+") as output:
    count = 0
    for username in user_list:    
        if username not in fetched_list:
            print("[%d] Fetching tweets for %s" % (count, username))
            username_tweets_to_csv(username, 0)    
            output.write('%s\n' % username)
        else:
            print("User %s already fetched. Skipping" % username)

        count += 1
