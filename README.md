# BOT Baby - A tweet generator app that is trained on left-wing and right-wing Indian twitter.
User needs to provide an initial prompt after which the app completes the rest of the tweet for the two sides.

Deployed at: http://botbaby.in/

The code is organized into 4 components:
1) [Twitter](twitter)
2) [Training](training/notebook)
3) [Deployment](deployment)
4) [Front-end](front-end)

## 1) Twitter
This contains the code to download tweets using a combination of [tweepy](https://www.tweepy.org/) and [GetOldTweets3](https://pypi.org/project/GetOldTweets3/). Sadly i came across [twint](https://github.com/twintproject/twint) later else I would have used that. Since tweepy only allowed fetching tweets in the last 30 days, I use GetOldTweets3 to get tweets as far back as 2014. 

To generate my dataset of left-wing (LW) and right-wing (RW) tweets, I start with 30-35 of famous personalities which the other side claims to be LW or RW. I then retrieve follower list of all these personalities and sort them in order. Idea is that anybody who follows most of these personalities belong to the same camp. I make use of GetOldTweets3 to download tweets for these users. 

To deal with rate limits better while downloading follower list, I fetch user ID instead of username. This gives 15x speed-up (45000 IDs vs 3000 usernames). I convert these user IDs to usernames using twitter's HTTP GET API that doesn't enforce any rate limits (https://twitter.com/intent/user?user_id=xxxxx). I have to do this as GetOldTweets3 only works on usernames and not user IDs. Once I have the usernames, I can use GetOldTweets3 to download tweets upto 2014.
Once I have all the tweets, I merge them all into a single file to do text-processing. I remove all hyperlinks, non-english characters, HTML markers etc. I also get rid of duplicate tweets and tweets below a certain length. I did shuffle earlier but later felt it is better not to do it since it is better for the language model if related tweets are next to each other.

Once I have my dataset ready I upload it to my google drive to train it on Google Colab.

### Files:
1. [notebooks/get_twitter_followers.ipynb](twitter/notebooks/get_twitter_followers.ipynb): Main notebook to download data from twitter using tweepy and GetOldTweets3
2. [scripts/](twitter/scripts): Individual python scripts most of which got merged into get_twitter_followers.ipynb. You don't need to use these.

## 2) Training
I am using Google Colab for training. I have subscribed to Colab Pro so i get a more powerful GPU along with more RAM.
I am using Max Woolf's excellent [notebook](https://minimaxir.com/2020/01/twitter-gpt2-bot/). I tried training my language model from scratch including on TPU, but it didn't give me as good a result as this notebook did, right out of the box.
I train two separate language models for LW & RW each. 

### Files: 
1. [Train_a_GPT_2_Model_on_Tweets.ipynb](training/notebook/Train_a_GPT_2_Model_on_Tweets.ipynb): Notebook to train GPT2-Model on Google Colab

## 3) Deployment
For deployment I decided to go with AWS, since I had free credits available and also because I found a nice blog [Deploying a pretrained GPT-2 model on AWS](https://www.kdnuggets.com/2019/12/deploying-pretrained-gpt-2-model-aws.html) that provided with basic scaffolding. I have improved on this and this is what my current deployment architecture looks like. 

TBD

I have an API gateway that forwards requests to a lambda function. The lambda first checks if the prompt is present in DynamoDB. If it finds it there then it directly returns the response back. Else it enqueues the requests into an SQS queue and launches a GPU g4dn.xlarge instance. The instance upon starting, reads from the queue, does the inferencing and adds the result into DynamoDB. The lambda waits for results to be added into DynamoDB, fetches it when available and returns the response back.

### Files: 
1. [find_sentiment.py](deployment/app/find_sentiment.py): Sample script to perform batch sentiment analysis using AWS Comprehend.
2. [gpt2-app.py](deployment/app/gpt2-app.py): Main backend app that runs a web app to do the inferencing
3. [gpt2-script.py](deployment/app/gpt2-script.py): Run inferencing as a python script. (DEPRECATED. Use gpt2-app.py)
4. [process_queue.py](deployment/app/process_queue.py): Read messages from an SQS Queue (FIFO) and trigger the inferencing
5. [run_inference.py](deployment/app/run_inference.py): Simple script to trigger inferencing directly on the GPU instance

6. [shutdown_script.sh](deployment/app/shutdown_script.sh): Script that gets called when instance is shutdown
7. [update_file_s3.sh](deployment/app/update_file_s3.sh): Download the latest prompts file from S3, update it with new additions and push it back
8. [lambda.py](deployment/lambda/lambda.py): Lambda function to trigger inferencing when needed else read from DynamoDB
9. [service/](deployment/service): Systemd service files to launch gpt2-app.py, process_queue.py at startup and shutdown_script.sh during shutdown

## 4) Front-end
For twitter UI, I made use of [Let's Build: With Tailwind CSS - Tweet](https://web-crunch.com/posts/lets-build-tailwind-css-tweet). Thank You [Andy Leverenz](https://twitter.com/webcrunchblog) for providing the basic building block. Also thanks to [Manan](https://github.com/manan2002) who enhanced it to make it into side-by-side view along with few other contributions. The website is hosted on S3 (Refer [Hosting a Static Website on Amazon S3](https://docs.aws.amazon.com/AmazonS3/latest/dev/WebsiteHosting.html)). The website provides auto-completion to the entered prompt to make user select one of the existing prompts. This not only gives a much faster response but also keeps the cost of inferencing down. Finally, the UI displays the tweets that belong to the majority class (Positive, Negative or Neutral) and color-codes them for better visibility.

