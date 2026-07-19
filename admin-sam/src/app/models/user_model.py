import bcrypt
import string
import secrets
import time
from .model import Model
from ..services import dynamo_service
from .. import MyError


class UserModel(Model):
    TableName = 'ClawEC2Users'
    TokenGSI = ('tokenGSI', 'token')
    Fields = ['email', 'encryptedPassword', 'token', 'tokenUsedAt', 'createdAt', 'updatedAt']

    def token_expired(self):
        return int(time.time()) - self.tokenUsedAt > 24 * 60 * 60
    
    def update_token(self):
        new_token = secrets.token_urlsafe(64)
        self.token = new_token
        timestamp = int(time.time())
        self.tokenUsedAt = timestamp
        self.updatedAt = timestamp
        table = dynamo_service.get_table(UserModel.TableName)
        dynamo_service.update_item(table, 'email', self.email, {
            'token': new_token,
            'tokenUsedAt': self.tokenUsedAt,
            'updatedAt': self.updatedAt,
        })
        return new_token
    
    def update_token_used_at(self):
        timestamp = int(time.time())
        table = dynamo_service.get_table(UserModel.TableName)
        dynamo_service.update_item(table, 'email', self.email, {
            'tokenUsedAt': timestamp
        })

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
    def auth_user(email, password):
        table = dynamo_service.get_table(UserModel.TableName)
        item = dynamo_service.get_item(table, 'email', email)
        if not item:
            raise MyError('The user does not exist.', 403)
        user = UserModel(item)
        if not user.encryptedPassword:
            raise MyError('Password not set.', 403)
        if bcrypt.checkpw(password.encode('utf-8'), user.encryptedPassword.encode('utf-8')):
            return user
        raise MyError('Failed to authenticate user.', 403)

    @staticmethod
    def get_by_email(email):
        table = dynamo_service.get_table(UserModel.TableName)
        item = dynamo_service.get_item(table, 'email', email)
        if item:
            return UserModel(item)
        return None

    @staticmethod
    def create(email):
        table = dynamo_service.get_table(UserModel.TableName)
        new_token = secrets.token_urlsafe(64)
        timestamp = int(time.time())
        new_user = {
            'email': email,
            'token': new_token,
            'tokenUsedAt': timestamp,
            'createdAt': timestamp,
            'updatedAt': timestamp
        }
        dynamo_service.create_item(table, new_user, 'email')
        item = dynamo_service.get_item(table, 'email', email)
        return UserModel(item)
