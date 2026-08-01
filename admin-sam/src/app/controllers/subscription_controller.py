import simplejson as json
from ..models.subscription_model import SubscriptionModel
from .. import MyError

def get_user_subscriptions(req):
    subscriptions = SubscriptionModel.get_user_subscriptions(req.user.id)
    return [sub.data for sub in subscriptions]

def create_subscription(req):
    subscription = SubscriptionModel.create_new(req.user.id)
    return subscription.data

def delete_subscription(req):
    user = req.user
    data = req.body
    subscription = SubscriptionModel.get_by_id(data['subscriptionId'])
    if user.id != subscription.userId:
        raise MyError('Only owner can delete!')
    if subscription.status != 'Not started':
        raise MyError('Only not started subscription can be deleted!')
    subscription.delete_subscription()
    return {'ok': True}
