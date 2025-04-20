resource "aws_ecr_repository" "watcher" {
  name = "watcher"
  force_delete = contains(["dev", "test", "staging"], var.stage)
}