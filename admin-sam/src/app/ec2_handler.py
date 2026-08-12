import json
import uuid
import random
import boto3
import time
import requests
import urllib.parse
import urllib.request
from .models.instance_model import InstanceModel


def handle_creation(event, context):
    """Handle EC2 instance creation requests."""
    body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event
    instance_id = body.get('id')
    if not instance_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing id in request body'})
        }

    instance_record = InstanceModel.get_by_id(instance_id)
    if not instance_record:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': f'Instance record {instance_id} not found'})
        }

    ec2 = boto3.client('ec2', region_name='us-west-2')

    instance_name = f"claw-{uuid.uuid4().hex[:8]}"

    # Get a subnet from the target VPC
    subnets = ec2.describe_subnets(
        Filters=[{'Name': 'vpc-id', 'Values': ['vpc-4387b026']}]
    )
    if not subnets['Subnets']:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No subnets found in vpc-4387b026'})
        }
    subnet_id = random.choice(subnets['Subnets'])['SubnetId']

    # Create a security group for this instance
    sg_name = f"{instance_name}-sg"
    sg = ec2.create_security_group(
        GroupName=sg_name,
        Description=f"Security group for {instance_name}",
        VpcId='vpc-4387b026',
    )
    sg_id = sg['GroupId']

    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'SSH'}]},
            {'IpProtocol': 'tcp', 'FromPort': 8000, 'ToPort': 8000,
             'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'App port 8000'}]},
            {'IpProtocol': 'tcp', 'FromPort': 18789, 'ToPort': 18789,
             'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': 'App port 18789'}]},
        ],
    )

    ec2.create_tags(
        Resources=[sg_id],
        Tags=[{'Key': 'Name', 'Value': sg_name}],
    )

    response = ec2.run_instances(
        ImageId=instance_record.imageId,
        InstanceType='t3.micro',
        KeyName='ClawEC2',
        SubnetId=subnet_id,
        SecurityGroupIds=[sg_id],
        MinCount=1,
        MaxCount=1,
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/xvda',
                'Ebs': {
                    'VolumeSize': 30,
                    'VolumeType': 'gp3',
                    'DeleteOnTermination': True,
                }
            }
        ],
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {'Key': 'Name', 'Value': instance_name}
                ]
            }
        ],
    )

    ec2_instance = response['Instances'][0]
    ec2_instance_id = ec2_instance['InstanceId']

    # Update the DDB record
    instance_record.update({
        'instanceId': ec2_instance_id,
        'instanceName': instance_name,
        'status': 'Initializing',
    })

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Instance created',
            'instanceId': ec2_instance_id,
            'name': instance_name,
        })
    }


def handle_check(event, context):
    """Check the status of an EC2 instance."""
    body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event
    instance_id = body.get('id')
    if not instance_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing id in request body'})
        }

    instance_record = InstanceModel.get_by_id(instance_id)
    if not instance_record:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': f'Instance record {instance_id} not found'})
        }

    ec2_instance_id = instance_record.instanceId
    if not ec2_instance_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No EC2 instance associated with this record'})
        }

    ec2 = boto3.client('ec2', region_name='us-west-2')

    # Check instance state
    instances = ec2.describe_instances(InstanceIds=[ec2_instance_id])
    instance_state = instances['Reservations'][0]['Instances'][0]['State']['Name']
    if instance_state != 'running':
        return {
            'statusCode': 200,
            'result': False,
            'body': json.dumps({'result': False, 'reason': f'Instance state is {instance_state}'})
        }

    # Check instance status (3/3 checks: system, instance, attached EBS)
    statuses = ec2.describe_instance_status(InstanceIds=[ec2_instance_id])
    if not statuses['InstanceStatuses']:
        return {
            'statusCode': 200,
            'result': False,
            'body': json.dumps({'result': False, 'reason': 'Status checks not yet available'})
        }

    status = statuses['InstanceStatuses'][0]
    system_status = status['SystemStatus']['Status']
    instance_status = status['InstanceStatus']['Status']
    attached_ebs_status = status.get('AttachedEbsStatus', {}).get('Status', 'ok')

    all_passed = (system_status == 'ok' and instance_status == 'ok' and attached_ebs_status == 'ok')

    return {
        'statusCode': 200,
        'result': all_passed,
        'body': json.dumps({
            'result': all_passed,
            'systemStatus': system_status,
            'instanceStatus': instance_status,
            'attachedEbsStatus': attached_ebs_status,
        })
    }


def handle_setup(event, context):
    """Set up an EC2 instance after it's running."""
    body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event
    instance_id = body.get('id')
    if not instance_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing id in request body'})
        }

    instance_record = InstanceModel.get_by_id(instance_id)
    if not instance_record:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': f'Instance record {instance_id} not found'})
        }

    ec2_instance_id = instance_record.instanceId
    instance_name = instance_record.instanceName
    load_balancer_arn = instance_record.loadBalancerArn
    domain = instance_record.domain
    claw_port = int(instance_record.clawPort)
    control_port = int(instance_record.controlPort)

    elbv2 = boto3.client('elbv2', region_name='us-west-2')
    acm = boto3.client('acm', region_name='us-west-2')

    # Get VPC from load balancer
    lb = elbv2.describe_load_balancers(LoadBalancerArns=[load_balancer_arn])
    vpc_id = lb['LoadBalancers'][0]['VpcId']

    # Find ACM certificate for the domain
    certs = acm.list_certificates(CertificateStatuses=['ISSUED'])
    cert_arn = None
    for cert in certs['CertificateSummaryList']:
        if cert['DomainName'] == domain or cert['DomainName'] == f'*.{domain}':
            cert_arn = cert['CertificateArn']
            break
    if not cert_arn:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'No ACM certificate found for domain {domain}'})
        }

    # Create target group for claw app (port 18789)
    tg_claw = elbv2.create_target_group(
        Name=instance_name,
        Protocol='HTTP',
        Port=18789,
        VpcId=vpc_id,
        TargetType='instance',
        HealthCheckProtocol='HTTP',
        HealthCheckPort='18789',
        HealthCheckPath='/',
    )
    tg_claw_arn = tg_claw['TargetGroups'][0]['TargetGroupArn']

    # Create target group for control (port 8000)
    tg_ctrl = elbv2.create_target_group(
        Name=f"{instance_name}-ctrl",
        Protocol='HTTP',
        Port=8000,
        VpcId=vpc_id,
        TargetType='instance',
        HealthCheckProtocol='HTTP',
        HealthCheckPort='8000',
        HealthCheckPath='/',
    )
    tg_ctrl_arn = tg_ctrl['TargetGroups'][0]['TargetGroupArn']

    # Register EC2 instance in both target groups
    elbv2.register_targets(
        TargetGroupArn=tg_claw_arn,
        Targets=[{'Id': ec2_instance_id}],
    )
    elbv2.register_targets(
        TargetGroupArn=tg_ctrl_arn,
        Targets=[{'Id': ec2_instance_id}],
    )

    # Create HTTPS listener for claw app
    elbv2.create_listener(
        LoadBalancerArn=load_balancer_arn,
        Protocol='HTTPS',
        Port=claw_port,
        Certificates=[{'CertificateArn': cert_arn}],
        DefaultActions=[{
            'Type': 'forward',
            'TargetGroupArn': tg_claw_arn,
        }],
    )

    # Create HTTPS listener for control
    elbv2.create_listener(
        LoadBalancerArn=load_balancer_arn,
        Protocol='HTTPS',
        Port=control_port,
        Certificates=[{'CertificateArn': cert_arn}],
        DefaultActions=[{
            'Type': 'forward',
            'TargetGroupArn': tg_ctrl_arn,
        }],
    )

    # Add inbound rules to the load balancer's security group
    ec2 = boto3.client('ec2', region_name='us-west-2')
    lb_sg_ids = lb['LoadBalancers'][0]['SecurityGroups']
    for sg_id in lb_sg_ids:
        ec2.authorize_security_group_ingress(
            GroupId=sg_id,
            IpPermissions=[
                {'IpProtocol': 'tcp', 'FromPort': claw_port, 'ToPort': claw_port,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': f'Claw app port {claw_port}'}]},
                {'IpProtocol': 'tcp', 'FromPort': control_port, 'ToPort': control_port,
                 'IpRanges': [{'CidrIp': '0.0.0.0/0', 'Description': f'Control port {control_port}'}]},
            ],
        )

    # Rotate tokens
    rotate_tokens(instance_record)

    # Update status to Active
    instance_record.update({'status': 'Active'})

    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Setup complete',
            'targetGroupClaw': tg_claw_arn,
            'targetGroupCtrl': tg_ctrl_arn,
        })
    }

def rotate_tokens(instance):
    time.sleep(10)
    try:
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        url = 'https://' + instance.domain + ':' + instance.controlPort + '/myapp/rotate-ec2-token/'
        payload = {"ec2Token": instance.ec2Token}
        response = requests.post(url, json=payload, headers=headers)
        resp = response.json()
        newEc2Token = resp['newEc2Token']
        instance.update({'ec2Token': newEc2Token})

        url = 'https://' + instance.domain + ':' + instance.controlPort + '/myapp/rotate-claw-token/'
        payload = {"ec2Token": newEc2Token}
        response = requests.post(url, json=payload, headers=headers)
        resp = response.json()
        clawToken = resp['clawToken']
        instance.update({'clawToken': clawToken})
    except Exception as e:
        print(f"Error rotating EC2 token: {e}")
        raise e
