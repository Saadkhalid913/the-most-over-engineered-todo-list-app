# Application secrets per environment.
# Secrets Manager has no "collections" — one JSON secret per env holds the key/value set.

locals {
  environments = toset(["dev", "prod"])

  # Placeholder keys for the stack we will wire later (RDS, etc.).
  app_secret_template = {
    DATABASE_URL = "mysql+pymysql://REPLACE_ME:REPLACE_ME@REPLACE_ME:3306/todos"
  }
}

resource "aws_secretsmanager_secret" "app" {
  for_each = local.environments

  name        = "${var.project_name}/${each.key}/app"
  description = "${var.project_name} ${each.key} application secrets (JSON key/value collection)"

  # 0 = destroy immediately (no 30-day recovery bill while learning).
  recovery_window_in_days = 0

  tags = {
    Environment = each.key
    Name        = "${var.project_name}/${each.key}/app"
  }
}

resource "aws_secretsmanager_secret_version" "app" {
  for_each = local.environments

  secret_id     = aws_secretsmanager_secret.app[each.key].id
  secret_string = jsonencode(local.app_secret_template)

  # Allow rotating/filling values outside Terraform without thrash on every apply.
  lifecycle {
    ignore_changes = [secret_string]
  }
}
