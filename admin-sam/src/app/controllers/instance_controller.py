import os, time
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
