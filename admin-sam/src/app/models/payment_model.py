import uuid
import time
from .model import Model
from ..services import dynamo_service
from .. import MyError
from decimal import Decimal


class PaymentModel(Model):
    TableName = 'ClawPayments'
    SubscriptionIdGSI = ('subscriptionIdGSI', 'subscriptionId')
    CheckoutSessionIdGSI = ('CheckoutSessionIdGSI', 'checkoutSessionId')
    # status: Pending | Paid
    Fields = ['id', 'subscriptionId', 'checkoutSessionId', 'userId', 'status', 'months', 'paymentAmount', 'createdAt', 'updatedAt']

    def delete_subscription(self):
        table = dynamo_service.get_table(PaymentModel.TableName)
        dynamo_service.delete_item(table, 'id', self.id) 
    
    def change_status(self, status):
        table = dynamo_service.get_table(PaymentModel.TableName)
        timestamp = int(time.time())
        dynamo_service.update_item(table, 'id', self.id, {
            'status': status,
            'updatedAt': timestamp,
        })

    @staticmethod
    def get_by_id(id):
        table = dynamo_service.get_table(PaymentModel.TableName)
        item = dynamo_service.get_item(table, 'id', id)
        if item:
            return PaymentModel(item)
        return None

    @staticmethod
    def get_by_checkout_session_id(checkout_session_id):
        table = dynamo_service.get_table(PaymentModel.TableName)
        items = dynamo_service.query(table, PaymentModel.CheckoutSessionIdGSI[0], PaymentModel.CheckoutSessionIdGSI[1], checkout_session_id)
        if items and len(items):
            return PaymentModel(items[0])
        return None

    @staticmethod
    def create_new(user_id, subscription_id, checkout_session_id, months, payment_amount):
        table = dynamo_service.get_table(PaymentModel.TableName)
        id = str(uuid.uuid4())
        timestamp = int(time.time())
        new_payment = {
            'id': id,
            'name': 'New subscription',
            'userId': user_id,
            'subscriptionId': subscription_id,
            'checkoutSessionId': checkout_session_id,
            'status': 'Pending',
            'months': months,
            'paymentAmount': payment_amount,
            'createdAt': timestamp,
            'updatedAt': timestamp,
        }
        dynamo_service.create_item(table, new_payment, 'id')
        item = dynamo_service.get_item(table, 'id', id)
        return PaymentModel(item)
