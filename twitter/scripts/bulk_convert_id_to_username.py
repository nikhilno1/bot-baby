import requests
import sys
import re

found = not_found = 0
user_list = []

print("Reading ID file");
with open("../right/all_followers_id_dedup.txt") as f:
    id_list = [line.rstrip() for line in f]

last_index = id_list.index("713723491657261056")
del id_list[0:last_index+1]
#sys.exit()

with open("../right/all_followers_username.txt", "a+") as output:
    count = last_index+1
    for user_id in id_list:
        print("[%d] Converting %s" % (count, user_id) , end=' ');
        r = requests.get('https://twitter.com/intent/user?user_id=' + user_id)
        user_search=re.search('<title>.*\(@(.*)\).*</title>', r.content.decode('utf-8'), re.IGNORECASE)
        if user_search:
            username = user_search.group(1)            
            user_list.append(username)
            output.write('%s\n' % username)
            found += 1            
            print("=> %s" % username);
        else:
            not_found += 1
            print("ID %s not found" % user_id);
        count += 1

    print("%d usernames found. %d not found." % (found, not_found))   
