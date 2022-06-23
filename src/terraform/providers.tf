provider "aws" {
  region = var.lambda-region
  alias  = "lambda-region"
}

provider "archive" {
  alias = "archive"
}
