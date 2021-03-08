from flask import request
from functools import wraps
from jose import jwt
import requests
from .config import *

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


## Auth Header


def get_token_auth_header():
    auth_header = request.headers.get("Authorization", None)
    if auth_header is None:
        raise AuthError(
            {
                "code": "authorization_header_missing",
                "description": "Authorization header is expected"
            }, 401)

    parts = auth_header.split()

    if parts[0].lower() != "bearer":
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Authorization header must start with"
                               " Bearer"
            }, 401)
    elif len(parts) == 1:
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Token not found"
            }, 401)
    elif len(parts) > 2:
        raise AuthError(
            {
                "code": "invalid_header",
                "description": "Authorization header must be"
                               " Bearer token"
            }, 401)

    token = parts[1]
    return token


def check_permissions(permission, payload):
    if 'permissions' in payload:
        permissions = payload["permissions"]
        if permission not in permissions:
            raise AuthError(
                {
                    'code': 'invalid_permissions',
                    'description': 'User does not have enough privileges'
                }, 401)
        else:
            return True
    else:
        raise AuthError(
            {
                'code': 'invalid_permissions',
                'description': 'User does not have any roles attached'
            }, 401)


def verify_decode_jwt(token):
    known_keys = requests.get(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json').json()
    unverified_header = jwt.get_unverified_header(token)
    if 'kid' not in unverified_header:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Authorization malformed.'
            }, 401)

    for key in known_keys['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = key
            break
    else:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

    try:
        payload = jwt.decode(token,
                             rsa_key,
                             algorithms=ALGORITHMS,
                             audience=API_AUDIENCE,
                             issuer='https://' + AUTH0_DOMAIN + '/')
        return payload

    except jwt.ExpiredSignatureError:
        raise AuthError(
            {
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

    except jwt.JWTClaimsError:
        raise AuthError(
            {
                'code':
                    'invalid_claims',
                'description':
                    'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
    except Exception:
        raise AuthError(
            {
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper

    return requires_auth_decorator
