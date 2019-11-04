try:
    from flask import Flask
    from flask_oidc import OpenIDConnect
except:
    raise ImportError("Unable to access Flask")

app = Flask(__name__)
#oidc = OpenIDConnect(app)

from app import routes