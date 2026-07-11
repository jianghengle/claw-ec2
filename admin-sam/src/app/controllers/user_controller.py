import simplejson as json
from .. import MyError


def ping(req):
    return {'pinged': True}

