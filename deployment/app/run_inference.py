# Simple script to trigger inferencing directly on the GPU instance

import urllib.parse
import os

import sys, getopt

def do_inference(prompt):
    prompt_url = urllib.parse.quote(prompt) 
    #print(prompt_url)
    ports = [8081,8082]
    for port in ports:
        cmd=f"curl --location --request GET 'http://127.0.0.1:{port}?prompt={prompt_url}&num_samples=20&batch_size=20&length=60&temperature=0.7&top_p=0.9&top_k=40' --header 'Content-Type: application/json'"
        print(cmd)
        os.system(cmd)

def main(argv):
    prompts_file = ''
    prompt = ''
    try:
        opts, args = getopt.getopt(argv,"hf:p:",["file=","prompt="])
    except getopt.GetoptError:
        print('run_inference.py [-f <prompts-file>] [-p <prompt>]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('run_inference.py [-f <prompts-file>] [-p <prompt>]')
            sys.exit()
        elif opt in ("-f", "--file"):
            prompts_file = arg
            #print('Prompts file is %s' % prompts_file)
        elif opt in ("-p", "--prompt"):
            prompt = arg
            #print('Prompt is %s' % arg)

    if prompt:
        do_inference(prompt)
    elif prompts_file:
        with open(prompts_file) as f:
            prompts_list = [line.rstrip() for line in f]    
            for prompt in prompts_list:
                do_inference(prompt)
    else:
        print('Error: Specify at least one parameter.\nUsage: run_inference.py [-f <prompts-file>] [-p <prompt>]')

if __name__ == "__main__":
   main(sys.argv[1:])
