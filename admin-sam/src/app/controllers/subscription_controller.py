import simplejson as json
from ..models.subscription_model import SubscriptionModel
from ..models.payment_model import PaymentModel
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

def get_subscription(req, sub_id):
    subscription = SubscriptionModel.get_by_id(sub_id)
    return subscription.data

def update_name(req, sub_id):
    subscription = SubscriptionModel.get_by_id(sub_id)
    new_name = req.body['name']
    subscription.update_name(new_name)
    subscription = SubscriptionModel.get_by_id(sub_id)
    return subscription.data

def get_sub_payments(req, sub_id):
    payments_data = []
    for p in PaymentModel.get_by_subscription_id(sub_id):
        if p.status == 'Paid':
            payments_data.append(p.data)
    return payments_data

