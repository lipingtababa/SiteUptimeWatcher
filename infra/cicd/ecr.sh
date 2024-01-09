AWS_REGION=us-east-1
repo_name=detector
aws ecr create-repository --repository-name $repo_name --region $AWS_REGION