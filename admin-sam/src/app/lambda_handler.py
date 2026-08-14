from . import MyError
from .my_http import MyReq, MyResp
from .controllers import user_controller
from .controllers import subscription_controller
from .controllers import stripe_controller
from .controllers import instance_controller


class MyRouter:
    def __init__(self, path_handlers):
        self.path_handlers = path_handlers

    def route(self, req):
        req_method = req.method
        if req_method == 'OPTIONS':
            return MyResp()

        if req.path.startswith('/stripe/'):
            return stripe_controller.handle(req)

        req_path_parts = self.split_path(req.path)
        for (method, path, auth_required, handler) in self.path_handlers:
            if req_method != method:
                continue
            (match, params) = self.path_match(req_path_parts, self.split_path(path))
            if match:
                if auth_required:
                    if (not req.user) or (req.user.token_expired()):
                        raise MyError('Failed to authenticate the user', 403)
                    req.user.update_token_used_at()
                return MyResp(handler(req, *params))
        raise MyError('Did not find the handler', 404)

    def path_match(self, req_path_parts, handler_path_parts):
        params = []
        if len(req_path_parts) != len(handler_path_parts):
            return (False, None)
        for i in range(len(req_path_parts)):
            req_path_part = req_path_parts[i]
            handler_path_part = handler_path_parts[i]
            if handler_path_part.startswith(':'):
                params.append(req_path_part)
            elif handler_path_part != req_path_part:
                return (False, None)
        return (True, tuple(params))

    def split_path(self, path):
        parts = []
        for s in path.split('/'):
            part = s.strip()
            if part:
                parts.append(part)
        return parts



def handle(event, context):
    try:
        req = MyReq(event)
        router = MyRouter([
            ('GET', '/ping', False, user_controller.ping),
            ('POST', '/send-login-link', False, user_controller.send_login_link),
            ('POST', '/verify-token', False, user_controller.verify_token),
            ('GET', '/get-user-subscriptions', True, subscription_controller.get_user_subscriptions),
            ('POST', '/create-subscription', True, subscription_controller.create_subscription),
            ('POST', '/delete-subscription', True, subscription_controller.delete_subscription),
            ('GET', '/get-subscription/:sub_id', True, subscription_controller.get_subscription),
            ('POST', '/update-sub-name/:sub_id', True, subscription_controller.update_name),
            ('GET', '/get-sub-payments/:sub_id', True, subscription_controller.get_sub_payments),
            ('POST', '/create-subscription-instance', True, instance_controller.create_subscription_instance),
            ('GET', '/get-sub-instance/:sub_id', True, instance_controller.get_sub_instance),
            ('POST', '/set-sub-claude-key', True, instance_controller.set_sub_claude_key),
        ])
        return router.route(req)
    except MyError as err:
        print('MyError: ' + err.message )
        return MyResp({ 'err': err.message }, err.code)
    except Exception as e:
        print(e)
        return MyResp({ 'err': str(e) }, 500)
