# Scaffold — ECS / ALB / RDS / CloudFront land in later PRs.
# Secrets for dev + prod are created now (see secrets.tf).
#
# Per-env stack applies (when compute exists) use:
#   terraform workspace select dev   # or prod
#   terraform apply -var-file=envs/dev.tfvars

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}
