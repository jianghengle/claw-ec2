import os, time, uuid
from .model import Model
from ..services import dynamo_service
from .. import MyError
from decimal import Decimal

DEFAULT_IMAGE_ID = os.environ.get('EC2_IMAGE_ID', '')
DEFAULT_BALANCER = os.environ.get('EC2_BALANCER', '')
DEFAULT_EC2_TOKEN = os.environ.get('EC2_TOKEN', '')
DEFAULT_DOMAIN = os.environ.get('EC2_DOMAIN', '')


class InstanceModel(Model):
    TableName = 'ClawInstances'
    # status: Creating | Initializing | Active
    Fields = ['id', 'status', 'ordinal', 'imageId', 'instanceId', 'instanceName', 'loadBalancerArn', 'ec2Token', 'clawToken', 'claudeKey', 'domain', 'controlPort', 'clawPort', 'createdAt', 'updatedAt']

    
    def update(self, updates):
        table = dynamo_service.get_table(InstanceModel.TableName)
        timestamp = int(time.time())
        updates['updatedAt'] = timestamp
        dynamo_service.update_item(table, 'id', self.id, updates)

    @staticmethod
    def get_by_id(id):
        table = dynamo_service.get_table(InstanceModel.TableName)
        item = dynamo_service.get_item(table, 'id', id)
        if item:
            return InstanceModel(item)
        return None

    @staticmethod
    def get_max_ordinal():
        table = dynamo_service.get_table(InstanceModel.TableName)
        items = dynamo_service.scan(table)
        max_ordinal = 0
        if items:
            for item in items:
                if item['ordinal'] > max_ordinal:
                    max_ordinal = item['ordinal']
        return max_ordinal

    @staticmethod
    def create_new():
        table = dynamo_service.get_table(InstanceModel.TableName)
        id = str(uuid.uuid4())
        timestamp = int(time.time())
        max_ordinal = InstanceModel.get_max_ordinal()
        new_ordinal = max_ordinal + 1
        new_item = {
            'id': id,
            'ordinal': new_ordinal,
            'imageId': DEFAULT_IMAGE_ID,
            'instanceId': '',
            'instanceName': '',
            'status': 'Creating',
            'loadBalancerArn': DEFAULT_BALANCER,
            'ec2Token': DEFAULT_EC2_TOKEN,
            'clawToken': '',
            'claudeKey': '',
            'domain': DEFAULT_DOMAIN,
            'controlPort': str(8000 + new_ordinal),
            'clawPort': str(9000 + new_ordinal),
            'createdAt': timestamp,
            'updatedAt': timestamp,
        }
        dynamo_service.create_item(table, new_item, 'id')
        item = dynamo_service.get_item(table, 'id', id)
        return InstanceModel(item)
