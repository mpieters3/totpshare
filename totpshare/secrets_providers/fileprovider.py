import binascii
import base64
import hashlib
import abc
import os
import logging
import tempfile
import os.path
from . import secretsprovider, secretslist, secretsmetadata

try:
    from Crypto.Cipher import AES
    from Crypto import Random
except:
    raise ImportError("Unable to access Crypto")

log = logging.getLogger('fileprovider')
DEFAULT_KEY = 'A string that should never be used'

class provider(secretsprovider):
    """ A file based provider for key lookup. Uses symmetric key encryption to avoid having them
    in plain text
     """

    def __init__(self):
        key = os.getenv('TOTPSHARE_FILE_ENCKEY', DEFAULT_KEY)
        if(key == DEFAULT_KEY):
            log.warn("No TOTPSHARE_FILE_ENCKEY found, secrets will be stored with the default key")

        self._block_size = AES.block_size
        self._key = hashlib.sha256(key.encode()).digest()

        self._path = os.getenv('TOTPSHARE_FILE_PATH')
        if(not self._path):
            self._path = tempfile.mkdtemp(prefix='totp_')
            log.debug("Temp folder created at %s", self._path)
     
    def get_secret(self, key_id: str) -> str:
        key_id = key_id.strip("\\//") #make sure stuck in current path
        with open(os.path.join(self._path, key_id.strip("\\//")), "rb") as f:
            enc_secret = f.read()
            enc_secret = base64.b64decode(enc_secret)
            iv = enc_secret[:self._block_size]
            cipher = AES.new(self._key, AES.MODE_CBC, iv)
            secret = self._unpad(cipher.decrypt(enc_secret[self._block_size:])).decode('utf-8')
            return secret

    def list_keys(self) -> secretslist:
        secretsList = []
        for f in os.listdir(self._path):
            try:
                secretsList.append(_parse_file_name(f))
            except:
                ##lets log and move on; rather return valid records still
                log.error("Found an invalid file in temp storage %s", f)
        return secretsList

    def add_key(self, metadata: secretsmetadata, secret: str) -> str:
        file_name = _build_file_name(metadata)
        secret = self._pad(secret)
        iv = Random.new().read(self._block_size)
        cipher = AES.new(self._key, AES.MODE_CBC, iv)
        encrypted_secret = base64.b64encode(iv + cipher.encrypt(secret.encode("utf8")))

        with open(os.path.join(self._path, file_name), "wb") as f:
            f.write(encrypted_secret)
        return file_name

    def delete_key(self, key_id: str):
        pass

    def _pad(self, s):
        return s + (self._block_size - len(s) % self._block_size) * chr(self._block_size - len(s) % self._block_size)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

def _build_file_name(metadata : secretsmetadata) -> str:
    """ Calculates what the file name is for the provided metadata
        the filename will be hex({metadata.id}).hex({metadata.display_name}).
        Underscores will be escaped with double underscores if in either field

        :param metadata: the metadata to convert.

    """
    return metadata.id.encode().hex() + "." + metadata.display_name.encode().hex()

def _parse_file_name(file_name: str) -> secretsmetadata:
    """ Calculates metadata from the file name
        this is done by decoding the two hex components outlined in _build_file_name
    """
    id_hex, display_name_hex = file_name.split(".")
    return secretsmetadata(bytes.fromhex(id_hex).decode('ascii'), bytes.fromhex(display_name_hex).decode('utf-8'), file_name)