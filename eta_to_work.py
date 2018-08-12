import json
import os
import urllib2
import boto3

def lambda_handler(event, context):
    start_from = os.environ['start_from']
    going_to = os.environ['going_to']
    google_api_key = os.environ['google_api_key']
    google_directions_url = 'https://maps.googleapis.com/maps/api/directions/json?origin=' + start_from.replace(' ', '+') + '&destination=' + going_to.replace(' ', '+') + '4&key=' + google_api_key
    sns_target_arn = os.environ['sns_target_arn']  # whom to inform if ETA is more than desired
    desired_eta_in_mins = os.environ['desired_eta_in_mins']
    html_request = urllib2.Request(google_directions_url)
    response = urllib2.urlopen(html_request)
    response_text = json.loads(response.read())
    eta_in_mins = (response_text['routes'][0]['legs'][0]['duration']['text']).split(' ')[0]

    #Send SNS message to me if ETA to work is greater than 30 minutes
    if int(eta_in_mins) > int(desired_eta_in_mins):
        message = "ETA to " + going_to + " is " + eta_in_mins + " minutes. Leave early"
        sns_client = boto3.client('sns', region_name='us-east-1')
        sns_response = sns_client.publish(
            TargetArn=sns_target_arn,
            Message=message,
            MessageStructure='text'
        )
