# Scaffold only — ECS / ALB / RDS / CloudFront land in later PRs.
# This data source proves AWS credentials + provider wiring without creating billable resources.

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}
