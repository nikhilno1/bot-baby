import glob
import os
import time

path = r'/home/nikhil/packages/GetOldTweets3/bin/tweets/' # use your path
all_files = glob.glob(path + "/*.csv")

for filename in all_files:
    statinfo = os.stat(filename)
    if statinfo.st_size is 84:
        filename = os.path.basename(filename)
        #print("%s is having size 84" % filename)
        handle=filename.split('_20')[0]
        year=filename.split('.csv')[0][-4:]
        #print("Re-fetching for %s & %s" % (handle, year))
        outfile = handle + "_" + year + ".csv"
        cmd = "/home/nikhil/packages/GetOldTweets3/bin/GetOldTweets3 --username " + handle + \
        " --since " + year + "-01-01" + " --until " + year + "-12-31" + \
        " --maxtweets 0 --emoji unicode --output /home/nikhil/packages/GetOldTweets3/bin/tweets/" + outfile 
        print(cmd)
        os.system(cmd)
        print("%s Done." % outfile)
        time.sleep(60)

