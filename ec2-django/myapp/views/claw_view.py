import os
import uuid
import re
import secrets
from datetime import datetime, timezone, timedelta
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from . import *

EC2_TOKEN_FILE = '/home/.claw_django/ec2_token'


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


def check_ec2_token(ec2_token):
    file_path = EC2_TOKEN_FILE
    if not file_exists(file_path):
        raise PermissionDenied({'error': 'Access Denied. No file.'})

    if run_cmd('cat ' + file_path).strip() != ec2_token:
        raise PermissionDenied({'error': 'Access Denied. Invalid token.'})

