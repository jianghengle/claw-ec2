import bcrypt
import string
import uuid
import secrets
import time
from .model import Model
from ..services import dynamo_service
from .. import MyError


class UserModel(Model):
    TableName = 'ClawUsers'
    EmailGSI = ('emailGSI', 'email')
    TokenGSI = ('tokenGSI', 'token')
    Fields = ['id', 'email', 'encryptedPassword', 'token', 'tokenUsedAt', 'createdAt', 'updatedAt']

    def token_expired(self):
        return int(time.time()) - self.tokenUsedAt > 24 * 60 * 60
    
    def update_token(self):
        new_token = secrets.token_urlsafe(64)
        self.token = new_token
        timestamp = int(time.time())
        self.tokenUsedAt = timestamp
        self.updatedAt = timestamp
        table = dynamo_service.get_table(UserModel.TableName)
        dynamo_service.update_item(table, 'id', self.id, {
            'token': new_token,
            'tokenUsedAt': self.tokenUsedAt,
            'updatedAt': self.updatedAt,
        })
        return new_token
    
    def update_token_used_at(self):
        timestamp = int(time.time())
        table = dynamo_service.get_table(UserModel.TableName)
        dynamo_service.update_item(table, 'id', self.id, {
            'tokenUsedAt': timestamp
        })

    @staticmethod
    def get_by_id(id):
        table = dynamo_service.get_table(UserModel.TableName)
        item = dynamo_service.get_item(table, 'id', id)
        if item:
            return UserModel(item)
        return None

    @staticmethod
    def get_by_email(email):
        if not email:
            raise MyError('No email')
        table = dynamo_service.get_table(UserModel.TableName)
        items = dynamo_service.query(table, UserModel.EmailGSI[0], UserModel.EmailGSI[1], email)
        if not len(items):
            return None
        if len(items) > 1:
            print('Found multiple users with same email')
            return None
        user = UserModel(items[0])
        return user

    @staticmethod
    def get_by_token(token):
        if not token:
            raise MyError('No token')
        table = dynamo_service.get_table(UserModel.TableName)
        items = dynamo_service.query(table, UserModel.TokenGSI[0], UserModel.TokenGSI[1], token)
        if not len(items):
            return None
        if len(items) > 1:
            print('Found multiple users with same token')
            return None
        user = UserModel(items[0])
        return user

    @staticmethod
    def create(email):
        table = dynamo_service.get_table(UserModel.TableName)
        id = str(uuid.uuid4())
        new_token = secrets.token_urlsafe(64)
        timestamp = int(time.time())
        new_user = {
            'id': id,
            'email': email,
            'token': new_token,
            'tokenUsedAt': timestamp,
            'createdAt': timestamp,
            'updatedAt': timestamp
        }
        dynamo_service.create_item(table, new_user, 'id')
        item = dynamo_service.get_item(table, 'id', id)
        return UserModel(item)
