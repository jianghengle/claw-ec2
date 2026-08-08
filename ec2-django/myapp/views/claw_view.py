import os, json
import time
import sqlite3
import secrets
from datetime import datetime, timezone, timedelta
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.exceptions import PermissionDenied
from . import *

EC2_TOKEN_FILE = '/home/ubuntu/.claw_django/ec2_token'
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
    with open(EC2_TOKEN_FILE, "w", encoding="utf-8") as file:
        file.write(new_ec2_token)
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
    claw_config = get_claw_config()
    claw_config['gateway']['auth']['token'] = new_claw_token
    with open(CLAW_JSON_FILE, 'w', encoding="utf-8") as file:
        json.dump(claw_config, file, indent=4, sort_keys=True)
    return Response({'clawToken': new_claw_token})


@api_view(['POST'])
def set_claude_key(request):
    ec2_token = request.data['ec2Token']
    check_ec2_token(ec2_token)
    claude_key = request.data['claudeKey']
    update_claude_key(claude_key)
    run_cmd_only('systemctl --user restart openclaw-gateway.service')
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


def update_claude_key(key):
    store_db = '/home/ubuntu/.openclaw/agents/main/agent/openclaw-agent.sqlite'
    sql = 'UPDATE auth_profile_store SET store_json = ?, updated_at = ? WHERE store_key = ?'
    store = {
        'version': 1,
        'profiles': {
            'anthropic:default': {
                'type': 'api_key',
                'provider': 'anthropic',
                'key': key
            },
            'anthropic:manual': {
                'type': 'api_key',
                'provider': 'anthropic',
                'key': key
            }
        }
    }
    store_json = json.dumps(store)
    timestamp = int(time.time() * 1000)
    with sqlite3.connect(store_db) as conn:
        cur = conn.cursor()
        cur.execute(sql, (store_json, timestamp, id,))
        conn.commit()
