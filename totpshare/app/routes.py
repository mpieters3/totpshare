from app import app#, oidc
from secrets_providers import get_provider, secretsmetadata, secretsprovider
from .token import get_token
try:
    from flask import Flask, request, jsonify, render_template
except:
    raise ImportError("Unable to access Crypto.Cipher")

secrets = get_provider()

@app.route('/')
def index():
    return render_template('index.html', secrets=secrets.list_keys())

@app.route('/secret/<string:key>')
def view_secret(key: str):
    key = secrets.get_secret(key)
    token, time_remaining = get_token(key)
    return render_template('secret.html', token=token, time_remaining=time_remaining)

@app.route('/api/secrets', methods=['GET'])
def list_secrets():
    return jsonify([e.serialize() for e in secrets.list_keys()]), 200

@app.route('/api/secrets', methods=['POST'])
#@oidc.accept_token()
def add_secret():
    data = request.get_json()
    id = secrets.add_key(secretsmetadata(data['id'],data['display_name']), data['key'])
    return jsonify({'key': id}), 200

@app.route('/api/secrets/<string:key>', methods=['GET'])
#@oidc.accept_token()
def get_secret(key: str):
    key = secrets.get_secret(key)
    token, time_remaining = get_token(key)
    return jsonify({
        'token': token,
        'time_remaining': time_remaining
    })