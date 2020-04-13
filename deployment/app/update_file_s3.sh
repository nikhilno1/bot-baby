#!/bin/bash

# Download the latest prompts file from S3, update it with new additions and push it back

aws s3 cp s3://botbaby.in/files/prompts.txt /home/ubuntu/prompts_temp.txt
sort /home/ubuntu/new_prompts.txt |uniq > /home/ubuntu/unique_prompts.txt
cat /home/ubuntu/unique_prompts.txt >> /home/ubuntu/prompts_temp.txt
aws s3 cp /home/ubuntu/prompts_temp.txt s3://botbaby.in/files/prompts.txt
rm /home/ubuntu/new_prompts.txt /home/ubuntu/unique_prompts.txt /home/ubuntu/prompts_temp.txt
