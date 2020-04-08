import urllib.parse
import os

input_file = "prompts.txt"
with open(input_file) as f:
    prompts_list = [line.rstrip() for line in f]    
    for prompt in prompts_list:
        prompt_url = urllib.parse.quote(prompt) 
        #print(prompt_url)
        ports = [8081,8082]
        for port in ports:
            cmd=f"curl --location --request GET 'http://127.0.0.1:{port}?prompt={prompt_url}&num_samples=20&batch_size=20&length=60&temperature=0.7&top_p=0.9&top_k=40' --header 'Content-Type: application/json'"
            print(cmd)
            os.system(cmd)

