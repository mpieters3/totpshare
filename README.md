# totpshare
Deals with securing a shared topt (one time code) factors. Allows the storage of TOPT keys for AWS behind a simple site, which can then have authn/authz placed in front of it to manage who has access

This is ultimately for a bad premise, but helps to enable MFA on things such as AWS root account that may have to be shared with multiple people. This allows limiting who can potentially get access to it.

## Design
Very simple design - use a basic storage solution (file backed for now) to put the provided keys in. Then use pyotp for when the user attempts to request the token to display what the current code is. 

## Getting Started
Fairly straightforward flask app.

export FLASK_APP=totpshare.py
flask run

## Configuration Options
minimal configuration

### fileprovider secrets
fileprovider is the simple, and only, storage option at present.

TOTPSHARE_FILE_ENCKEY to an encryption key that you want used for the secrets; this will be used to encrypt the stored secrets at rest. If not set, a default key is used.
TOTPSHARE_FILE_PATH to a file path (must already exist) where you want the keys and metadata to be stored. if not set, a temporary folder is created (which means every restart you will no longer have your keys from a previous run)
