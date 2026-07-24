output "aws_account_id" {
  description = "Account Terraform is authenticated to"
  value       = data.aws_caller_identity.current.account_id
}

output "aws_caller_arn" {
  description = "IAM principal used by Terraform"
  value       = data.aws_caller_identity.current.arn
}

output "aws_region" {
  description = "Region the AWS provider is targeting"
  value       = data.aws_region.current.name
}
