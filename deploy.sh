#! /bin/bash

rm -rf .terraform
terraform init terraform/common
terraform apply -auto-approve terraform/common

rm -rf .terraform
terraform init terraform/workspace
terraform workspace select $1 terraform/workspace
terraform apply -auto-approve terraform/workspace
