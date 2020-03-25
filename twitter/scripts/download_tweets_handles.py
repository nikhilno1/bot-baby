import GetOldTweets3 as got
import pandas as pd
import os
import sys
import time

since_list=['2014-01-01', '2015-01-01', '2016-01-01', '2017-01-01', '2018-01-01', '2019-01-01', '2020-01-01']
until_list=['2014-12-31', '2015-12-31', '2016-12-31', '2017-12-31', '2018-12-31', '2019-12-31', '2020-12-31']

print("Exiting..")
sys.exit()

with open("/home/nikhil/packages/GetOldTweets3/bin/right_handles.txt") as f:
    handles = [line.rstrip() for line in f]

for handle in handles:
    print("Getting tweets for " + handle)

    for since, until in zip(since_list, until_list):
        outfile = handle + "_" + since.split('-')[0] + ".csv"
        cmd = "/home/nikhil/packages/GetOldTweets3/bin/GetOldTweets3 --username " + handle + \
        " --since " + since + " --until " + until + \
        " --maxtweets 0 --emoji unicode --output /home/nikhil/packages/GetOldTweets3/bin/tweets/" + outfile
        print(cmd)
        os.system(cmd)
        print("%s Done." % outfile)
        time.sleep(60)
