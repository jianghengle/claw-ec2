import os, time
import requests
from ..models.subscription_model import SubscriptionModel
from ..models.instance_model import InstanceModel
from ..services.step_function_service import start_sm_execution
from .. import MyError

STATE_MACHINE_ARN = os.environ['EC2_STATE_MACHINE']

def create_subscription_instance(req):
    user = req.user
    data = req.body
    subscription = SubscriptionModel.get_by_id(data['subscriptionId'])
    if user.id != subscription.userId:
        raise MyError('Only subscription owner can create instance!')
    timestamp = int(time.time())
    if subscription.status != 'Active' or subscription.endTime < timestamp:
        raise MyError('Subscription must be active and not expired!')
    if subscription.instanceId:
        raise MyError('Subscription already has an instance!')
    instance = InstanceModel.create_new()
    subscription.update_instance_id(instance.id)
    start_sm_execution(STATE_MACHINE_ARN, {'id': instance.id})
    return instance.data

def get_sub_instance(req, sub_id):
    user = req.user
    subscription = SubscriptionModel.get_by_id(sub_id)
    if user.id != subscription.userId:
        raise MyError('Only subscription owner can get the instance!')
    if not subscription.instanceId:
        raise MyError('No instance id on subscription')
    instance = InstanceModel.get_by_id(subscription.instanceId)
    return instance.data

def set_sub_claude_key(req):
    user = req.user
    data = req.body
    subscription = SubscriptionModel.get_by_id(data['subscriptionId'])
    if user.id != subscription.userId:
        raise MyError('Only subscription owner can create instance!')
    if not subscription.instanceId:
        raise MyError('No instance id on subscription')
    instance = InstanceModel.get_by_id(subscription.instanceId)
    send_claude_key(instance, data['claudeKey'])
    instance.update({'claudeKey': 'set'})
    time.sleep(5)
    return {'ok': True}

def send_claude_key(instance, key):
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    url = 'https://' + instance.domain + ':' + instance.controlPort + '/myapp/set-claude-key/'
    payload = {
        "ec2Token": instance.ec2Token,
        "claudeKey": key,
    }
    requests.post(url, json=payload, headers=headers)
