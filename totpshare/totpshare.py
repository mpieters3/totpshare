try:
    from flask import Flask, session
    from flask_session import Session
    from flask_oidc import OpenIDConnect
    from flask_wtf.csrf import CSRFProtect
    from jinja2 import Template
except:
    raise ImportError("Unable to access Flask")

from totpshare.config import Config, OIDC_CREATE_SECRETS
from totpshare.secrets_providers import Secrets
from tempfile import mkstemp
import os

class CredStorage:
    """
    Session based storage for the OIDC credential details
    """
    def __setitem__(self, sub, item):
        session[sub] = item

    def __getitem__(self, sub):
        return session[sub]

credstorage = CredStorage()

app = Flask(__name__, instance_relative_config=True)
app.config.from_object(Config)
app.config.update({
    'OIDC_CREDENTIALS_STORE': credstorage
})
app.config.from_pyfile('application.cfg', silent=True)

## Let's build the client secrets file
if(app.config['OIDC_CLIENT_SECRETS'] == OIDC_CREATE_SECRETS):
    with open('client_secrets.json.dict') as file_:
        template = Template(file_.read())
    client_secrets = template.render(
        oidc_provider=app.config['OIDC_PROVIDER'], 
        oidc_client_id=app.config['OIDC_CLIENT_ID'],
        oidc_client_secret=app.config['OIDC_CLIENT_SECRET_KEY'])    
    fd, temp_secrets = mkstemp()
    os.write(fd, str.encode(client_secrets))
    os.close(fd)
    app.config['OIDC_CLIENT_SECRETS'] = temp_secrets

sess = Session(app)
csrf = CSRFProtect(app)
oidc = OpenIDConnect(app)
secrets = Secrets(app)

from totpshare import routes