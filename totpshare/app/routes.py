from app import app
from secrets_providers import get_provider, secretsmetadata, secretsprovider
from .token import get_token
try:
    from flask import Flask, request, jsonify
except:
    raise ImportError("Unable to access Crypto.Cipher")

secrets = get_provider()

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/api/secrets', methods=['GET'])
def list_secrets():
    return jsonify({'secrets': [e.serialize() for e in secrets.list_keys()]}), 200

@app.route('/api/secrets', methods=['POST'])
def add_secret():
    data = request.get_json()
    id = secrets.add_key(secretsmetadata(data['id'],data['display_name']), data['key'])
    return jsonify({'key': id}), 200

@app.route('/api/secrets/<string:key>', methods=['GET'])
def get_secret(key):
    key = secrets.get_secret(key)
    token, time_remaining = get_token(key)
    return jsonify({
        'token': token,
        'time_remaining': time_remaining
    })