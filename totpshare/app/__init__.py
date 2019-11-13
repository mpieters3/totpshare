try:
    from flask import Flask
    from flask_oidc import OpenIDConnect
except:
    raise ImportError("Unable to access Flask")

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

#oidc = OpenIDConnect(app)

from app import routes