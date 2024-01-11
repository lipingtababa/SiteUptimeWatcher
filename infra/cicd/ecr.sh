#！/bin/bash

# Create identity provider for github


# Create github role with proper permissions and conditions


# Create ECR repository

AWS_REGION=us-east-1
repo_name=watcher
aws ecr create-repository --repository-name $repo_name --region $AWS_REGION