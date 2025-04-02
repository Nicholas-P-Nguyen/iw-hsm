from azure.identity import DefaultAzureCredential
import azure.keyvault.keys as keys
import azure.keyvault.keys.crypto as crypto
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import base64
import os

VAULT_URL = os.environ["https://COSIW11.vault.azure.net/"]
credential = DefaultAzureCredential()
client = keys.KeyClient(vault_url=VAULT_URL, credential=credential)

# Global Variables
RSA_BIT_SIZE = 2048
AES_BYTE_SIZE = 32
IV_BYTE_SIZE = 16
BLOCK_BIT_SIZE = 128

#-----------------------------------------------------------------------
# Functions to create, get, and delete keys.
#-----------------------------------------------------------------------

# Create a RSA key of any type. If a key with the same name already 
# exists, a new version of that key is created.
def create_RSA(key_name: str):
    rsa_key = client.create_rsa_key(key_name, size=RSA_BIT_SIZE)
    return rsa_key

def retrieve_key(key_name: str):
    key = client.get_key(key_name)
    return key

def delete_key(key_name: str):
    deleted_key = client.begin_delete_key(key_name).result()
    return deleted_key

def get_deleted_date(deleted_key: keys.DeletedKey):
    return deleted_key.deleted_date

#-----------------------------------------------------------------------
# Cryptographic operations
#-----------------------------------------------------------------------
def encrypt(key_name: str, file_path: str):
    # Generating random AES key
    aes_key = os.urandom(AES_BYTE_SIZE)
    # Random salt for encryption
    iv = os.urandom(IV_BYTE_SIZE)

    # Opening clients file
    with open(file_path, "rb") as f:
        data = f.read()

    # Setting up AES Encryption Algorithm
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    encryptor = cipher.encryptor()

    # Padding block size
    padder = padding.PKCS7(BLOCK_BIT_SIZE).padder()
    padded_data = padder.update(data) + padder.finalize()

    # Encryting clients file using AES key
    cipher_text = encryptor.update(padded_data) + encryptor.finalize()

    # Encrypting the AES key using the RSA key
    rsa_key = create_RSA(key_name)
    crypto_client = crypto.CryptographyClient(rsa_key, credential=credential)

    encrypted_key = crypto_client.encrypt(crypto.EncryptionAlgorithm.rsa_oaep, aes_key).ciphertext
    
    # TODO: add a check here to see if client wants us to store a backup in our database
    # Client needs the encrypted key, IV, and ciphertext to decrypt their files
    return {
        "encrypted_key": base64.b64encode(encrypted_key).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ciphertext": base64.b64encode(cipher_text).decode()
    }

