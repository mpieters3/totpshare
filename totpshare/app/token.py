try:
    import pyotp
except:
    raise ImportError("Unable to access Crypto.Cipher")
import time

def get_token(secret: str):
    ''' 
        Returns the current pin for the provided secret, 
        along with how much time is remaining for the current secret
    '''
    totp = pyotp.TOTP(secret)
    return (totp.now(), (totp.interval-(int(round(time.time())) % totp.interval)))