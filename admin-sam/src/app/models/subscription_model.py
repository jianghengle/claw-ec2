import uuid
import time
from .model import Model
from ..services import dynamo_service
from .. import MyError
from decimal import Decimal
from datetime import datetime
from dateutil.relativedelta import relativedelta


def add_months_time(start_time, months):
    date = datetime.fromtimestamp(start_time)
    new_date = date + relativedelta(months=months)
    end_time = int(new_date.timestamp())
    return end_time

class SubscriptionModel(Model):
    TableName = 'ClawSubscriptions'
    UserIdGSI = ('userIdGSI', 'userId')
    # status: Not started | Active
    Fields = ['id', 'name', 'userId', 'instanceId', 'startTime', 'endTime', 'status', 'createdAt', 'updatedAt']

    def delete_subscription(self):
        table = dynamo_service.get_table(SubscriptionModel.TableName)
        dynamo_service.delete_item(table, 'id', self.id)
        
    def add_months(self, months):
        table = dynamo_service.get_table(SubscriptionModel.TableName)
        timestamp = int(time.time())
        updates = {'updatedAt': timestamp}
        if self.startTime:
            end_time = add_months_time(self.endTime, months)
            updates['endTime'] = end_time
        else:
            end_time = add_months_time(timestamp, months)
            updates['startTime'] = timestamp
            updates['endTime'] = end_time
            updates['status'] = 'Active'
        dynamo_service.update_item(table, 'id', self.id, updates)

    def update_name(self, new_name):
        table = dynamo_service.get_table(SubscriptionModel.TableName)
        timestamp = int(time.time())
        updates = {
            'name': new_name,
            'updatedAt': timestamp,
        }
        dynamo_service.update_item(table, 'id', self.id, updates)

    @staticmethod
    def get_by_id(id):
        table = dynamo_service.get_table(SubscriptionModel.TableName)
        item = dynamo_service.get_item(table, 'id', id)
        if item:
            return SubscriptionModel(item)
        return None

    @staticmethod
    def get_user_subscriptions(user_id):
        table = dynamo_service.get_table(SubscriptionModel.TableName)
        items = dynamo_service.query(table, SubscriptionModel.UserIdGSI[0], SubscriptionModel.UserIdGSI[1], user_id)
        return [SubscriptionModel(item) for item in items]

    @staticmethod
    def create_new(user_id):
        table = dynamo_service.get_table(SubscriptionModel.TableName)
        id = str(uuid.uuid4())
        timestamp = int(time.time())
        new_subscription = {
            'id': id,
            'name': 'New subscription',
            'userId': user_id,
            'status': 'Not started',
            'createdAt': timestamp,
            'updatedAt': timestamp,
        }
        dynamo_service.create_item(table, new_subscription, 'id')
        item = dynamo_service.get_item(table, 'id', id)
        return SubscriptionModel(item)
