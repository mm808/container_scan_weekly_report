data "archive_file" "python-lambda-package" {
  provider    = archive
  type        = "zip"
  source_file = "${path.module}/../function_code/lambda_function.py"
  output_path = "lambda_function.zip"
}

resource "aws_lambda_function" "weekly-image-scan-function" {
  provider         = aws.lambda-region
  function_name    = var.lambda-function-name
  description      = "checks weekly on the container image scan results"
  filename         = "lambda_function.zip"
  source_code_hash = data.archive_file.python-lambda-package.output_base64sha256
  role             = aws_iam_role.weekly-image-scan-role.arn
  runtime          = "python3.8"
  handler          = "lambda_function.lambda_handler"
  timeout          = 300
}
