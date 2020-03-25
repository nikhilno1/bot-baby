import requests
import sys
import re

user_id = sys.argv[1]
r = requests.get('https://twitter.com/intent/user?user_id=' + user_id)

#print(r.content)

user_search=re.search('<title>.*\(@(.*)\).*</title>', r.content.decode('utf-8'), re.IGNORECASE)
if user_search:
    username = user_search.group(1)
    print(user_id + "=" + username)
else:
    print("not found")


