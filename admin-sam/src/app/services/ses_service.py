import boto3

SENDER = "Bee-Archi <system@bee-archi.com>"

AWS_REGION = "us-west-2"        

CHARSET = "UTF-8"

def send_email(recipents, subject, body_text, body_html):
    client = boto3.client('ses', region_name="us-west-2")
    client.send_email(
        Destination={
            'ToAddresses': recipents,
        },
        Message={
            'Body': {
                'Html': {
                    'Charset': CHARSET,
                    'Data': body_html,
                },
                'Text': {
                    'Charset': CHARSET,
                    'Data': body_text,
                },
            },
            'Subject': {
                'Charset': CHARSET,
                'Data': subject,
            },
        },
        Source=SENDER,
    )
