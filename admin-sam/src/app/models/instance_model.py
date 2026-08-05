import uuid
import time
from .model import Model
from ..services import dynamo_service
from .. import MyError
from decimal import Decimal


class InstanceModel(Model):
    TableName = 'ClawInstances'
    # status: Creating | Active
    Fields = ['id', 'status', 'ec2Id', 'ec2Token', 'clawToken', 'claudeKey', 'domain', 'controlPort', 'clawPort', 'createdAt', 'updatedAt']

    
    def change_status(self, status):
        table = dynamo_service.get_table(InstanceModel.TableName)
        timestamp = int(time.time())
        dynamo_service.update_item(table, 'id', self.id, {
            'status': status,
            'updatedAt': timestamp,
        })

    @staticmethod
    def get_by_id(id):
        table = dynamo_service.get_table(InstanceModel.TableName)
        item = dynamo_service.get_item(table, 'id', id)
        if item:
            return InstanceModel(item)
        return None

    @staticmethod
    def create_new():
        table = dynamo_service.get_table(InstanceModel.TableName)
        id = str(uuid.uuid4())
        timestamp = int(time.time())
        new_item = {
            'id': id,
            'status': 'Creating',
            'ec2Id': '',
            'ec2Token': '',
            'clawToken': '',
            'claudeKey': '',
            'domain': '',
            'controlPort': '',
            'clawPort': '',
            'createdAt': timestamp,
            'updatedAt': timestamp,
        }
        dynamo_service.create_item(table, new_item, 'id')
        item = dynamo_service.get_item(table, 'id', id)
        return InstanceModel(item)
