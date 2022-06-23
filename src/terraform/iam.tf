resource "aws_iam_role" "weekly-image-scan-role" {
  provider = aws.lambda-region
  name     = "weekly_image_scan_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_policy" "weekly-image-scan-lambda-policy" {
  provider    = aws.lambda-region
  name        = "weekly-image-scan-lambda-policy"
  path        = "/"
  description = "IAM policy for logging from a lambda"

  policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*",
      "Effect": "Allow"
    },
    {
      "Action": [
          "ses:SendEmail",
          "ses:SendRawEmail"
      ],
      "Resource": "*",
      "Effect": "Allow"
    },
    {
      "Action": [
          "ecr:DescribeImageScanFindings",
          "ecr:DescribeRegistry",
          "ecr:DescribePullThroughCacheRules",
          "ecr:DescribeImages",
          "ecr:DescribeRepositories",
          "ecr:ListImages"
        ],
      "Resource": "*",
      "Effect": "Allow"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "weekly-image-scan-lambda-attach" {
  provider   = aws.lambda-region
  role       = aws_iam_role.weekly-image-scan-role.name
  policy_arn = aws_iam_policy.weekly-image-scan-lambda-policy.arn
}
