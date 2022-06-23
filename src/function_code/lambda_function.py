from datetime import datetime, timezone, timedelta
import boto3
from botocore.exceptions import ClientError

# Global Vars #
ecr_client = boto3.client('ecr')
dev_registryId='012345678910' # aws account id

# get the date one week ago to use for target scan results
def get_last_week():
    lastWeekDateTime = datetime.now(timezone.utc) - timedelta(days =7)
    return lastWeekDateTime

# get all repositories in the registry
def get_repos(registry_id):
    rep_list = []
    try:
        # get all repositories
        response = ecr_client.describe_repositories(registryId=registry_id)
        repos = response['repositories']
        while "NextToken" in response:
            response = ecr_client.describe_repositories(registryId=registry_id, NextToken=response['NextToken'])
            repos.extend(response['repositories'])
        for item in repos:
            repo_name = item['repositoryName']
            rep_list.append(repo_name)
    except Exception as e:
        print(f"Error getting all repos: {str(e)}")
        exit(1)
    else:
        print("Completed getting all repos:")
        for rname in rep_list:
            print(f"   {rname}")

    return rep_list

# get all the images created in last week with Critical or High severity security issues
def get_new_images(dev_registryId, repos_list, date_time):
    itemlist = []
    di = ""
    image_paginator = ecr_client.get_paginator('describe_images')
    try:
        for r in repos_list:
            response_iterator = image_paginator.paginate(registryId=dev_registryId, repositoryName=r)
            for page in response_iterator:
                imageDetails = page["imageDetails"]
                for image in imageDetails:
                    if date_time <= image['imagePushedAt']:
                        if 'imageScanFindingsSummary' in image:
                            scan_finding = image['imageScanFindingsSummary']
                            sev_counts = scan_finding['findingSeverityCounts']
                            if 'CRITICAL' in sev_counts or 'HIGH' in sev_counts:
                                if 'imageTags' in image: # a few images were pushed without tags...
                                    di = {'imageName': image['repositoryName'], 'imageDigest': image['imageDigest'], 'imageTag': image['imageTags'][0], 'pushedDate': image['imagePushedAt']}
                                    itemlist.append(di)
        newlist = sorted(itemlist, key=lambda d: d['imageName'])

        # get only the newest of each image
        shortlist = []
        temp_item = newlist[0]
        last_item = newlist[len(newlist) - 1]
        for item in newlist:
            if item['imageName'] == temp_item['imageName']:
                if item['pushedDate'] > temp_item['pushedDate']:
                    temp_item = item
            elif item['imageName'] != temp_item['imageName']:
                shortlist.append(temp_item)
                temp_item = item

            if item == last_item:
                shortlist.append(item)

    except Exception as e:
        print(f"!Error getting new images: {str(e)}")
        exit(1)
    else:
        print("Completed finding new images:")
        for item in shortlist:
            print(f"   {item}")
    
    return shortlist

def get_scan_results(dev_registryId, new_image_list):
    itemlist = []
    scan_paginator = ecr_client.get_paginator('describe_image_scan_findings')
    try:
        for image in new_image_list:
            repo_name = image['imageName']
            image_digest = image['imageDigest']
            image_tag = image['imageTag']
            response_iterator = scan_paginator.paginate(
                registryId=dev_registryId,
                repositoryName=repo_name,
                imageId={
                    'imageDigest': image_digest,
                    'imageTag': image_tag
                }
            )
            for page in response_iterator:
                findings = page['imageScanFindings']['findings']
                for item in findings:
                    if item['severity'] == 'CRITICAL' or item['severity'] == 'HIGH':
                        image_id = (f"{repo_name}:{image_tag}")
                        sec_issue = {'imageName': image_id, 'issueSev': item['severity'], 'issueLink': item['uri']}
                        itemlist.append(sec_issue)

    except Exception as e:
        print(f"Error getting scan findings: {str(e)}")
        exit(1)
    else:
        print("Completed scan findings:")
        for item in itemlist:
            print(f"   {item}")

    return itemlist

# make text body for email
def format_email(scan_results):
    em_body = """The following are Critical and High level security issues found in images pushed in the last week.
    Please check each image repository and tag for the specific security issues and their remediation steps by following the link included.\n"""
    processed_image = ""
    for result in scan_results:
        if result['imageName'] != processed_image:
            em_body = em_body + "\n"
            image_txt = f"Image {result['imageName']} security issues:\n"
            issue_txt = f"   Issue severity: {result['issueSev']}.    Issue details link: {result['issueLink']}.\n"
            em_body = em_body + image_txt
            em_body = em_body + issue_txt
        else:
            issue_txt = issue_txt = f"   Issue severity: {result['issueSev']}.    Issue details link: {result['issueLink']}.\n"
            em_body = em_body + issue_txt
        
        processed_image = result['imageName']

    return em_body

# make html body for email
def format_html(scan_results):
    html_head = """The following are Critical and High level security issues found in images pushed in the last week. Please check each image repository and tag for the specific security issues and their remediation steps by following the link included."""
    html_doc = f"""<html>
    <head></head>
    <body>
    <h1></h1>
    <p>{html_head}</p>
    """
    processed_image = ""
    for result in scan_results:
        if result['imageName'] != processed_image:
            link = result['issueLink']
            html_doc = html_doc + f"<p>Image {result['imageName']} security issues:<br>&nbsp;&nbsp;Issue severity: {result['issueSev']}.&nbsp;{link}<br>"
        else:
            link = result['issueLink']
            html_doc = html_doc + f"&nbsp;&nbsp;Issue severity: {result['issueSev']}.&nbsp;{link}<br>"

        processed_image = result['imageName']

    # finalize html_doc
    html_doc = html_doc + "</body>\n" + "</html>\n"

    return html_doc

def send_email(email_body, html_body):
    from_address = "noreply@scan.report"
    to_address = ["user1@scan.report.com", "user2@scan.report.com"]
    aws_region = "us-east-1"
    email_subj = "Container image weekly scan report"
    email_charst = "UTF-8"

    ses_client = boto3.client('ses',region_name=aws_region)

    try:
        response = ses_client.send_email(
            Destination={'ToAddresses':to_address},
            Message={
                'Body': {
                    'Html': {
                        'Charset': email_charst,
                        'Data': html_body,
                    },
                    'Text': {
                        'Charset': email_charst,
                        'Data': email_body,
                    }
                },
                'Subject': {
                    'Charset': email_charst,
                    'Data': email_subj,
                },
            },  
            Source=from_address,
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['MessageId'])

def lambda_handler(event, context):
    target_date_time = get_last_week()
    print(f"One week ago date was: {target_date_time}")
    repos_list = get_repos(dev_registryId)
    new_image_list = get_new_images(dev_registryId, repos_list, target_date_time)
    
    if len(new_image_list) > 0:
        scan_results = get_scan_results(dev_registryId, new_image_list)
    else:
        print("No new images in the past week, done!")
        exit(0)
    
    if len(scan_results) > 0:
        email_body = format_email(scan_results)
        html_body = format_html(scan_results)
        send_email(email_body, html_body)
    else:
        print("No new images with security issues, done!")
        exit(0) 
