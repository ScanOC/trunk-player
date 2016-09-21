#!/usr/bin/env python
import tinys3
import sys
import os

filename = sys.argv[1]
location = sys.argv[2]
f_name = os.path.basename(filename)


# Creating a simple connection 
# Update with your S3 keys
conn = tinys3.Connection('ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ','ZZZZZZZZZZZZZZZZZZZZZZZZZ')

# Uploading a single file
try:
    f = open(filename,'rb')
    conn.upload(f_name,f,location)
    f.close()
except:
    print("Failed to upload file {} to s3".format(f_name))
else:
    os.remove(filename)
    print("File {} uploaded to s3".format(f_name))

