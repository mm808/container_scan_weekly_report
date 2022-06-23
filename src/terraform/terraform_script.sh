#!/bin/bash

if [ -z "$1" ]
then
  echo "you must provide TF_ACTION"
  exit 1
fi

TF_COMMAND=""

if [[ $1 = "plan" ]]
then
    TF_COMMAND=${TF_COMMAND:="terraform plan"}
elif [[ $1 = "apply" ]]
then
    TF_COMMAND=${TF_COMMAND:="terraform apply -auto-approve"}
else
    echo "No valid TF_ACTION provided!"
    exit 1
fi

terraform init
echo "Running $TF_COMMAND..."
${TF_COMMAND}
