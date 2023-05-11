#!/usr/bin/python3
"""
Pre-requisites:
1. python3 >= 3.9
2. aws-cli >= 2.8.9
3. virtualenv >= 20.4.3 (optional)
4. pip3 >= 23.0.1 (optional)
5. AWS SSO configured

Instruction:
1. Make sure you have the pre-requisites installed
2. Create a virtual environment (optional)
  2.1. `virtualenv -p python3 .env`
  2.2. `source .env/bin/activate`
3. Install the requirements
  3.1. `pip3 install boto3`
4. Run the script
  4.1. `python3 getssocred.py <profile_name>`

Example:
python3 getssocred.py myprofile
export AWS_ACCESS_KEY_ID=ASIA2GKAMM6VV3JDE3H6
export AWS_SECRET_ACCESS_KEY=dt5nZMEHUQtRVvR+Yh/De0BbQDuj6ryYivmUeyze
export AWS_SESSION_TOKEN=IQoJb3JpZ2luX2VjEHUaCWV1LXdlc3QtMSJGMEQCIC8I...

Notes: 
- This credentials are valid depending on the permission set assigned to the user.
- You can use this credentials to access AWS resources using the AWS CLI or a custom application.
"""
import os
import sys
import json
import boto3
import configparser

AWS_CONFIG=os.path.expanduser('~/.aws/config')
AWS_CACHE_DIR=os.path.expanduser('~/.aws/sso/cache')

def get_profile(profile: str) -> configparser.SectionProxy:
  #Get the AWS account ID for the given profile.
  config = configparser.ConfigParser()
  config.read(AWS_CONFIG)

  try:
    return config["profile {name}".format(name=profile)]
  except KeyError:
    raise KeyError("Profile {name} not found".format(name=profile))

def get_sso_token() -> str:
  #Get the SSO token from the newest cache file.

  dir_path = AWS_CACHE_DIR  
  list_of_files = os.listdir(dir_path)
  full_paths = [os.path.join(dir_path, file_name) for file_name in list_of_files]
  try:
    newest_file = max(full_paths, key=os.path.getctime)
  except Exception as err:
    raise err
  
  with open(newest_file, 'r') as f:
    data = json.load(f)
    return data['accessToken']

def get_aws_credentials(profile: str):
  #Print the temporary SSO credentials for the given profile.
  profile_data = get_profile(profile)
  
  sso = boto3.client('sso', region_name=profile_data['sso_region'])
  sso_token = get_sso_token()
  account_id = profile_data['sso_account_id']
  role_name = profile_data['sso_role_name']
  try:
    response = sso.get_role_credentials(
      roleName=role_name,
      accountId=account_id,
      accessToken=sso_token
    )
    print("export AWS_ACCESS_KEY_ID={}".format(response['roleCredentials']['accessKeyId']))
    print("export AWS_SECRET_ACCESS_KEY={}".format(response['roleCredentials']['secretAccessKey']))
    print("export AWS_SESSION_TOKEN={}".format(response['roleCredentials']['sessionToken']))
  except Exception as err:
      raise err

if __name__ == '__main__':
  if len(sys.argv) != 2:   
    print("wrong number of arguments.\nTo use the script: python getssocred.py <profile_name>\n")
    sys.exit(0)
  get_aws_credentials(sys.argv[1])