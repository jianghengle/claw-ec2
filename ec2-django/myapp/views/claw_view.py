import os
import uuid
import re
import secrets
from datetime import datetime, timezone, timedelta
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from . import *


@api_view(['POST'])
def verify_ec2_token(request):
    ec2_token = request.data['ec2Token']
    check_ec2_token(ec2_token)
    return Response({'ok': True})


def check_ec2_token(ec2_token):
    file_path = '/home/ubuntu/.claw_django/ec2_token'
    if not file_exists(file_path):
        raise PermissionDenied({'error': 'Access Denied. No file.'})

    if run_cmd('cat ' + file_path).strip() != ec2_token:
        raise PermissionDenied({'error': 'Access Denied. Invalid token.'})

