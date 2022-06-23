# Container Scan Weekly Report #

This project creates a lambda that will run weekly and look for any container image scans that found Critical or High security vulnerabilities in the scan items of am AWS ECR.   
It then generates a report and emails it. Use this to help development teams improve the security posture of their container images.

### Useful links / methods used in the code ###
[ECR describe_images](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr.html#ECR.Client.describe_images)    
[ECR describe_image_scan_findings](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/ecr.html#ECR.Client.describe_image_scan_findings)

### Design    
The project is a lambda run on an weekly schedule. It is set up using Terraform and uses the archive and aws modules. When you run terraform plan it will generate the new zip file for deployment. There are .tf files that create the CloudWatch logs and IAM items related to the lambda. The state file is saved in a s3 bucket backend.

### Deployment    
The buildspec.yml file included is designed to work in a AWS CodeBuild project. It runs in a default CodeBuild runner and installs TerraForm at the beginning of the process. It then calls the terraform_script.sh to run either the _plan_ command or _apply_ command. I originally used this with a Jenkins pipeline project that would pass the $TF_ACTION as a parameter set manually to start the build.
