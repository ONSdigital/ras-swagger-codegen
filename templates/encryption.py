##############################################################################
#                                                                            #
#   Simple AES256 Cryptographer routine to handle string encryption          #
#   Date:    21 May 2017                                                     #
#   Author:  Gareth Bult                                                     #
#   License: MIT                                                             #
#   Copyright (c) 2017 Crown Copyright (Office for National Statistics)      #
#                                                                            #
#   Initial peer review:                                                     #
#                                                                            #
#   Revision    Date    Reason                                               #
#                                                                            #
##############################################################################
from Crypto import Random
from Crypto.Cipher import AES
from hashlib import sha256
from base64 import b64encode, b64decode


class ONSCryptographer:
    """Manage the encryption and decryption of random byte strings"""

    def __init__(self, key):
        """
        Set up the encryption key, this will come from an .ini file or from
        an environment variable. Change the block size to suit the data supplied
        or performance required.

        :param key: The encryption key to use when encrypting the data 
        """
        self.bs = 16
        self.key = sha256(key.encode('utf-8')).digest()

    def pad(self, data):
        """
        Pad the data out to the selected block size.

        :param data: The data were trying to encrypt 
        :return: The data padded out to our given block size
        """
        vector = AES.block_size - len(data) % AES.block_size
        return data + ((bytes([vector])) * vector)
        # return data + (self.bs - len(data) % self.bs) * chr(self.bs - len(data) % self.bs

    def unpad(self, data):
        """
        Un-pad the selected data.

        :param data: Our padded data 
        :return: The data 'un'padded
        """
        return data[0:-data[-1]]

    def encrypt(self, raw_text):
        """
        Encrypt the supplied text

        :param raw_text: The data to encrypt, must be a string of type byte 
        :return: The encrypted text
        """
        raw_text = self.pad(raw_text)
        init_vector = Random.new().read(AES.block_size)
        ons_cipher = AES.new(self.key, AES.MODE_CBC, init_vector)
        return b64encode(init_vector + ons_cipher.encrypt(raw_text))

    def decrypt(self, encrypted_text):
        """
        Decrypt the supplied text

        :param encrypted_text: The data to decrypt, must be a string of type byte 
        :return: The unencrypted text
        """
        encrypted_text = b64decode(encrypted_text)
        init_vector = encrypted_text[:16]
        ons_cipher = AES.new(self.key, AES.MODE_CBC, init_vector)
        return self.unpad(ons_cipher.decrypt(encrypted_text[16:]))
