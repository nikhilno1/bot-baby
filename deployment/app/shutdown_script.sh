# Script that gets called when instance is shutdown.
# Currently we push all the new prompts to S3 to update auto-completion
#!/bin/bash

/home/ubuntu/update_file_s3.sh
