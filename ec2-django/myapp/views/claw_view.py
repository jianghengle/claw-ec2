import os, json
import uuid
import re
import secrets
from datetime import datetime, timezone, timedelta
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from . import *

EC2_TOKEN_FILE = '/home/.claw_django/ec2_token'
CLAW_JSON_FILE = '/home/ubuntu/.openclaw/openclaw.json'


@api_view(['POST'])
def verify_ec2_token(request):
    ec2_token = request.data['ec2Token']
    check_ec2_token(ec2_token)
    return Response({'ok': True})


@api_view(['POST'])
def rotate_ec2_token(request):
    ec2_token = request.data['ec2Token']
    check_ec2_token(ec2_token)
    new_ec2_token = secrets.token_urlsafe(64)
    run_cmd('echo "' + new_ec2_token + '" > ' + EC2_TOKEN_FILE)
    return Response({'newEc2Token': new_ec2_token})


@api_view(['POST'])
def get_claw_token(request):
    ec2_token = request.data['ec2Token']
    check_ec2_token(ec2_token)
    claw_config = get_claw_config()
    claw_token = claw_config['gateway']['auth']['token']
    return Response({'clawToken': claw_token})


@api_view(['POST'])
def rotate_claw_token(request):
    ec2_token = request.data['ec2Token']
    check_ec2_token(ec2_token)
    new_claw_token = secrets.token_urlsafe(32)
    run_cmd('openclaw config set gateway.auth.token "' + new_claw_token + '"')
    run_cmd('openclaw gateway restart')
    return Response({'clawToken': new_claw_token})


@api_view(['POST'])
def set_claude_key(request):
    ec2_token = request.data['ec2Token']
    check_ec2_token(ec2_token)
    claude_key = request.data['claudeKey']
    run_cmd('printf "%s\n" "' + claude_key + '" | openclaw models auth paste-api-key --provider anthropic')
    run_cmd('openclaw gateway restart')
    return Response({'ok': True})


def get_claw_config():
    if not file_exists(CLAW_JSON_FILE):
        raise PermissionDenied({'error': 'No openclaw.json file.'})
    claw_config = None
    try:
        with open(CLAW_JSON_FILE, 'r', encoding='utf-8') as file:
            claw_config = json.load(file)
    except Exception as e:
        print(e)
        raise PermissionDenied({'error': 'Cannot parse openclaw.json file.'})
    return claw_config


def check_ec2_token(ec2_token):
    file_path = EC2_TOKEN_FILE
    if not file_exists(file_path):
        raise PermissionDenied({'error': 'Access Denied. No file.'})

    if run_cmd('cat ' + file_path).strip() != ec2_token:
        raise PermissionDenied({'error': 'Access Denied. Invalid token.'})
