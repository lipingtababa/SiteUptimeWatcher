resource "aiven_pg" "postgres" {
  project      = var.aiven_project
  service_name = "the-pg"
  cloud_name   = "do-ams"
  plan         = "free-1-5gb"

  pg_user_config {
    pg_version = "16"
    timescaledb {
      max_background_workers = 16
    }
  }
}


# Store the database connection details in SSM Parameter Store
resource "aws_ssm_parameter" "db_host" {
  name  = "/watcher/postgre/host"
  type  = "String"
  value = aiven_pg.postgres.service_host
}

resource "aws_ssm_parameter" "db_port" {
  name  = "/watcher/postgre/port"
  type  = "String"
  value = aiven_pg.postgres.service_port
}

resource "aws_ssm_parameter" "db_name" {
  name  = "/watcher/postgre/name"
  type  = "String"
  value = "defaultdb"
}

resource "aws_ssm_parameter" "db_user" {
  name  = "/watcher/postgre/user"
  type  = "String"
  value = "avnadmin"
}

resource "aws_ssm_parameter" "db_password" {
  name  = "/watcher/postgre/password"
  type  = "SecureString"
  value = aiven_pg.postgres.service_password
}
