# totpshare
Deals with securing a shared topt (one time code) factors. Allows the storage of TOPT keys for AWS behind a simple site, which can then have authn/authz placed in front of it to manage who has access.

This is ultimately to help address something that shouldn't exist, but can MFA on things such as AWS root account that may have to be shared with multiple people. This allows limiting who can potentially get access to it, without requiring the physical hardware token model that inheritently puts limitings on physical location for who can access the root account (as well as other drawbacks to having a physical keychain of dozens to hundreds of hardware tokens!)

## Design
Front end that is secured and authenticated by OIDC, with an optional Administrators group that gives access to add or remove OPT seed keys.

Use a basic storage solution (file backed for now) to store the topt seed key when added. Users can then use the front end to get a generated token value for accessing the root accounts.

The seed key for the otp is not made available to either administrators or users of the system once loaded, so cannot be extracted and reused elsewhere by a current user. 

Written in Flask, Flask-WTF with bootstrap, as it wasn't worth while creating a fancy user experience here. Some left overs of endpoints for potential programmatic interaction still exist, but won't be used. 

## Getting Started
Fairly straightforward flask app; after setting the required configuration options below, launch as a flask application:
```
export FLASK_APP=totpshare.py
flask run
```

The application has two pages 
- '/Admin' where administrators can add new otp seeds, as well as delete existing ones
- '/' where users can pull the access tokens

## Configuration Options
This requires a few configuration options to be set

### OIDC Configuration
Uses either a client_secrets.json per (flask-oidc)[https://flask-oidc.readthedocs.io/en/latest/]. To simplify usage, a (client_secrets.json.dict)[./toptshare/client_secrets.json.dict] are in the repository to use as a reference, and we have environment configuration options to seed a client_secrets.json using jinja2, though its expected syntax may not work for all providers (but does work for okta, issuer and auth server must match for this to work)

- OIDC_CLIENT_SECRETS : either the path to a (client_secrets.json)[https://github.com/okta/samples-python-flask/blob/master/okta-hosted-login/client_secrets.json.dist] or set to GENERATED.
- AUTHZ_ADMIN : If set to a name, the 'groups' claim in the id token will be checked to see if the user is a member of this before allowing access to the 'Admin' page

#### GENERAtED
If OIDC_CLIENT_SECRETS is set to generated, the following parameters are used to generate a client_secrets.json, instead. 
- OIDC_PROVIDER : the auth server/issuer url (eg: https://dev-xxxxxx.okta.com/oauth2/default). if the issuer and auth server don't match, then this won't work
- OIDC_CLIENT_ID : the application client id
- OIDC_CLIENT_SECRET_KEY : the application client secret

### OIDC Provider Configuration
This should be configured as a standard Authorization Code flow application, per flask-oidc setup. Redirect uri's must correctly be set for your deployed instance. 

** if it's desired to use AUTHZ_ADMIN, the a 'groups' claim must be added to the id token that includes AUTHZ_ADMIN's value in it when the user should be an administrator **

### fileprovider
fileprovider is the simple, and only, storage option at present for the key factors. Puts metadata into the file name, and stores the actual keys in the generated files. There are better ways to do file storage, but this was fast and should not have an issues even in a multi-server environment (doesn't prevent duplicates, however)

- TOTPSHARE_FILE_PATH : where to store the files that are created (default: 'topt_keys/')
- TOTPSHARE_FILE_ENCKEY : to an encryption key that you want used for the secrets (default: 'A string that should never be used')

## Flask
Uses Flask Session to store group claims between restarts. SESSION_TYPE is defaulted to filesystem, but you can update this as appropriate for flask. SECRET_KEY should also be set to a none-default value

## Flaws
While this option does significantly limit who has access to the MFA token, there's still a flaw:
Whoever loads the token code will have been able to store that same key elsewhere and store it for use elsewhere, as well. 

This does already significantly reduce exposure and may be acceptable, but if further reduction is needed

### Potential mitigation for AWS
During root account onboarding, the party that sets up MFA will not be a member of the email distribution group who can reset the root password. That party can take the secret key, and load it into toptshare during initial account onboarding.

After that is done, the true Root Account administrators distribution group should rotate the root account password and validate the MFA token in toptshare again. When this is done, no one party has access to both authentication factors ever again (Root Account admin's can only get TOPT tokens, but can't reproduce the seed key)
