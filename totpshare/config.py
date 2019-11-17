import os

def str_to_bool(s):
    if s == 'True':
         return True
    elif s == 'False':
         return False
    else:
         raise ValueError # evil ValueError that doesn't tell you what the wrong value was

TOTP_SHARE_DEFAULT_KEY = 'A string that should never be used'
OIDC_CREATE_SECRETS = 'GENERATED'

class Config(object):
    """ Majority of properties that this app requires, with preferred defaults
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    ## We need persistent storage for session to let the OIDC auth work across restarts
    ## Use filesystem by default
    SESSION_TYPE = os.environ.get('SESSION_TYPE') or 'filesystem'
    SESSION_PERMANENT = str_to_bool(os.environ.get('SESSION_PERMANENT', 'True'))
    SESSION_COOKIE_SECURE = str_to_bool(os.environ.get('SESSION_COOKIE_SECURE', 'False'))
    SESSION_USE_SIGNER =  str_to_bool(os.environ.get('SESSION_USE_SIGNER', 'True'))
    OIDC_CALLBACK_ROUTE = os.environ.get('OIDC_CALLBACK_ROUTE') or '/authorization-code/callback'
    OIDC_SCOPES = os.environ.get('OIDC_SCOPES') or ["openid", "profile", "email"]
    OIDC_ID_TOKEN_COOKIE_SECURE = str_to_bool(os.environ.get('OIDC_ID_TOKEN_COOKIE_SECURE', 'False'))
    AUTHZ_ADMIN = os.environ.get('AUTHZ_ADMIN') or None
    TOTPSHARE_FILE_ENCKEY = os.getenv('TOTPSHARE_FILE_ENCKEY', TOTP_SHARE_DEFAULT_KEY)
    TOTPSHARE_FILE_PATH = os.getenv('TOTPSHARE_FILE_PATH') or 'topt_keys/'
    ## Having a separate client secret file to inject may be a hassle, so giving an alternate build
    ## of client_secrets.json for flask-oidc using the client_secrets.json.dict
    OIDC_CLIENT_SECRETS = os.environ.get('OIDC_CLIENT_SECRETS') or OIDC_CREATE_SECRETS
    OIDC_PROVIDER = os.getenv('OIDC_PROVIDER')
    OIDC_CLIENT_ID = os.getenv('OIDC_CLIENT_ID')
    OIDC_CLIENT_SECRET_KEY = os.getenv('OIDC_CLIENT_SECRET_KEY')