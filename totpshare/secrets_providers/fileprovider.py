import binascii
import base64
import abc
import os
import logging
import tempfile
import os.path
from . import secretsprovider, secretslist, secretsmetadata

try:
    from Crypto.Cipher import AES
except:
    raise ImportError("Unable to access Crypto.Cipher")

log = logging.getLogger('fileprovider')

class provider(secretsprovider):
    """ A file based provider for key lookup. Uses symmetric key encryption to avoid having them
    in plain text
     """

    def __init__(self):
        self._key = os.getenv('TOTPSHARE_FILE_ENCKEY')
        if(not self._key): 
            log.warn("No TOTPSHARE_FILE_ENCKEY found, secrets will be stored plain text")

        self._path = os.getenv('TOTPSHARE_FILE_PATH')
        if(not self._path):
            self._path = tempfile.mkdtemp(prefix='totp_')
            log.debug("Temp folder created at %s", self._path)
     
    def get_secret(self, key_id: str) -> str:
        key_id = key_id.strip("\\//") #make sure stuck in current path
        with open(os.path.join(self._path, key_id.strip("\\//")), "r") as f:
            enc_key = f.read()
            if(self._key):
                enc_key, iv = enc_key.split('|')
                decryptor = AES.new(self._key, AES.MODE_CBC, iv)
                enc_key = decryptor.decrypt(enc_key)

            return enc_key

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
        with open(os.path.join(self._path, file_name), "w") as f:
            f.write(secret)
        return file_name

    def delete_key(self, key_id: str):
        pass

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