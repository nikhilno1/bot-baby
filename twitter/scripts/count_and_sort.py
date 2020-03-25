# Python3 code to demonstrate 
# sorting and removal of duplicates 
# Using Counter.most_common() + list comprehension 
from collections import Counter 

# initializing list 
with open("../rightwing/all_followers_id.txt") as f:
    id_list = [line.rstrip() for line in f]

# printing original list 
print("Length of ids before sorting: %d" % len(id_list)) 

# using Counter.most_common() + list comprehension 
# sorting and removal of duplicates 
id_dedup = [key for key, value in Counter(id_list).most_common()] 

# print result 
print("Length of ids after sorting: %d" % len(id_dedup)) 
print("Percentage reduction: %d" % int((len(id_dedup)*100)/len(id_list)))
#print(id_dedup[0:10])
#print(id_dedup[-10:])

with open("../rightwing/all_followers_id_dedup.txt", "w") as output:
    for user_id in id_dedup:
        output.write('%s\n' % user_id)

