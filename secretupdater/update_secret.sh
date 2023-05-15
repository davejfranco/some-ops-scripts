#!/bin/bash

# This script updates a secret in AWS Secrets Manager. Given a secret name and a file containing the secret values
# The file must be in the format of key=value.

# Set the name of the secret to update
SECRET_NAME=$1 #Example: "staging/api-pdf/environment"

# Read the file containing secrets
FILE_PATH=$2 #Example: app.properties #"app.properties"

secret_dict="{}"

while IFS='=' read -r key value; do
  # Trim leading and trailing whitespace from key and value
  key=$(echo "$key" | awk '{$1=$1};1')
  value=$(echo "$value" | awk '{$1=$1};1')
  
  if [ -z "$key" ] || [[ $key == \#* ]]; then
    continue
  fi

  secret_dict=$(jq --arg k "$key" --arg v "$value" '.[$k] = $v' <<< "$secret_dict")
  
done < "$FILE_PATH"

aws secretsmanager update-secret \
  --secret-id "$SECRET_NAME" \
  --secret-string "$secret_dict"

# Check the exit code of the AWS CLI command
if [ $? -eq 0 ]; then
  echo "Secret updated successfully."
else
  echo "Failed to update secret."
fi





