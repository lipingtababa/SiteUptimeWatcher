provider "aws" {
  region = "us-east-1"
}

resource "aws_secretsmanager_secret" "default" {
  name = "/watcher/postgre/password"
}
