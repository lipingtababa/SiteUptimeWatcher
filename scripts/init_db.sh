#!/bin/bash

# Get database information from AWS SSM Parameter Store
echo "Fetching database configuration from AWS SSM Parameter Store..."
DB_HOST=$(aws ssm get-parameter \
    --name "/watcher/postgre/host" \
    --region us-east-1 \
    --query 'Parameter.Value' \
    --output text)

DB_USER=$(aws ssm get-parameter \
    --name "/watcher/postgre/user" \
    --region us-east-1 \
    --query 'Parameter.Value' \
    --output text)

DB_PASSWORD=$(aws ssm get-parameter \
    --name "/watcher/postgre/password" \
    --with-decryption \
    --region us-east-1 \
    --query 'Parameter.Value' \
    --output text)

DB_NAME=$(aws ssm get-parameter \
    --name "/watcher/postgre/name" \
    --region us-east-1 \
    --query 'Parameter.Value' \
    --output text)

DB_PORT=$(aws ssm get-parameter \
    --name "/watcher/postgre/port" \
    --region us-east-1 \
    --query 'Parameter.Value' \
    --output text)

# create endpoints table
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -p $DB_PORT << EOF
CREATE TABLE endpoints (
    id SERIAL PRIMARY KEY,
    url VARCHAR(255) NOT NULL,
    regex VARCHAR(255) NOT NULL,
    interval INT NOT NULL
);
EOF

# Connect to PostgreSQL and insert the sites
echo "Adding sites to database..."
PGPASSWORD=$DB_PASSWORD psql -h $DB_HOST -U $DB_USER -d $DB_NAME -p $DB_PORT << EOF
INSERT INTO endpoints (url, regex, interval) VALUES
    ('https://www.google.com', '.*', 60),
    ('https://www.github.com', '.*', 60),
    ('https://www.microsoft.com', '.*', 60),
    ('https://www.amazon.com', '.*', 60),
    ('https://www.nosuchsitewhateverahahhahaha.se', '.*', 60);
EOF

echo "Added sites to the database for monitoring:"
echo "- https://www.google.com"
echo "- https://www.github.com"
echo "- https://www.microsoft.com"
echo "- https://www.amazon.com"
echo "- https://www.nosuchsitewhateverahahhahaha.se" 