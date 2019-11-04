try:
    from flask import Flask
except:
    raise ImportError("Unable to access Crypto.Cipher")

app = Flask(__name__)

from app import routes