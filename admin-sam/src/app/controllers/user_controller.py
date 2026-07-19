import simplejson as json
from ..models.user_model import UserModel
from .. import MyError
from ..services import ses_service


def ping(req):
    return {'pinged': True}

def send_login_link(req):
    email = req.body['email']
    origin = req.body['origin']
    user = UserModel.get_by_email(email)
    if user:
        if user.token_expired():
            user.update_token()
        else:
            user.update_token_used_at()
    else:
        user = UserModel.create(email)
    send_login_email(user, origin)
    return {'ok': True}

def send_login_email(user, origin):
    login_link = origin + '?token=' + user.token
    body_text = 'Please click the link below to login Claw EC2:\n' + login_link
    body_html = '<html><body><p>Please click the link below to login Claw EC2:</p><p><a href=\"' + login_link + '\" target=\"_blank\">login</a></p></body></html>'
    recipents = [user.email]
    ses_service.send_email(recipents, 'Claw EC2 login', body_text, body_html)

def verify_token(req):
    if not req.user:
        raise MyError('Invalid token', 401)
    if req.user.token_expired():
        raise MyError('Token expired', 401)
    return {
        'email': req.user.email,
    }
