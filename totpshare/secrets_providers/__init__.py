import abc
from typing import List

class secretsmetadata:
    """ Encapsulates metadata of the secrets for viewing """
    def __init__(self, id: str, display_name: str, key: str = None):
        self.id = id
        self.display_name = display_name
        self.key = key
    
    def serialize(self):
        return {
            'id': self.id, 
            'display_name': self.display_name,
            'key': self.key
        }

## Using typing for fun
secretslist = List[secretsmetadata]

class secretsprovider(metaclass=abc.ABCMeta):
    """ Represents a source of secret topt keys """

    @abc.abstractmethod
    def get_secret(self, key_id: str) -> str:
        """ Retrieves a specific secret key

        :param key_id: The key identifier from list_keys
        """
        pass

    @abc.abstractmethod
    def list_keys(self) -> secretslist:
        """ List available keys, along with metadata """
        pass

    @abc.abstractmethod
    def add_key(self, metadata: secretsmetadata, key: str) -> str:
        """ Adds a new key into storage 
        
        returns key identifier

        :param metadata: metadata for the key
        :param key: the totp key
        """
        pass

    @abc.abstractmethod
    def delete_key(self, key_id: str) -> str:
        """ Removes a key (or archives it)

        returns key identifier

        :param key_id key to remove
        """
        pass

from . import fileprovider

def get_provider():
    """ Returns the provider to use for secret retrieval and storage """

    ## Hard code to file provider for now
    return fileprovider.provider()