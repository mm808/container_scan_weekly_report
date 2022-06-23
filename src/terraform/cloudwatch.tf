resource "aws_cloudwatch_log_group" "weekly-image-scan-lambda-log-group" {
  provider          = aws.lambda-region
  name              = "/aws/lambda/${var.lambda-function-name}"
  retention_in_days = 3
}

resource "aws_cloudwatch_event_rule" "weekly-image-scan-lambda-event" {
  provider            = aws.lambda-region
  name                = "run-lambda-function"
  description         = "Schedule lambda function"
  schedule_expression = "cron(00 12 ? * 1 *)"
}

resource "aws_cloudwatch_event_target" "weekly-image-scan-lambda-target" {
  provider  = aws.lambda-region
  target_id = "weekly_image_scan_lambda_target"
  rule      = aws_cloudwatch_event_rule.weekly-image-scan-lambda-event.name
  arn       = aws_lambda_function.weekly-image-scan-function.arn
}

resource "aws_lambda_permission" "allow-cloudwatch" {
  provider      = aws.lambda-region
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.weekly-image-scan-function.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.weekly-image-scan-lambda-event.arn
}
