terraform {
  required_version = "=1.1.3"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 4.0.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "= 2.2.0"
    }
  }

  backend "s3" {
    bucket = "tfstate-bucket"
    key    = "terraformstatefile"
    region = "us-east-1"
  }
}