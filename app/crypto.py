from azure.identity import DefaultAzureCredential
import azure.keyvault.keys as keys
import azure.keyvault.keys.crypto as crypto
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
import base64
import os
from dotenv import load_dotenv

load_dotenv()
VAULT_URL = os.getenv("VAULT_URL")
RSA_BIT_SIZE = int(os.getenv("RSA_BIT_SIZE", 2048))
AES_BYTE_SIZE = int(os.getenv("AES_BYTE_SIZE", 32))
IV_BYTE_SIZE = int(os.getenv("IV_BYTE_SIZE", 16))
BLOCK_BIT_SIZE = int(os.getenv("BLOCK_BIT_SIZE", 128))
MASTER_KEY = os.getenv("MASTER_KEY")

# Creating instance of Azure's key client
credential = DefaultAzureCredential()
client = keys.KeyClient(vault_url=VAULT_URL, credential=credential)

#-----------------------------------------------------------------------
# Functions to create, get, disable, and delete keys.
#-----------------------------------------------------------------------

# IMPORTANT: should only be called once by us to save money
# Create a RSA key of any type 
def create_RSA():
    rsa_key = client.create_rsa_key(MASTER_KEY, size=RSA_BIT_SIZE)
    return rsa_key

# Gets the master key
def retrieve_master_key():
    rsa_key = client.get_key(MASTER_KEY)
    return rsa_key

# IMPORTANT: Only call this when we know we're doing with this project
# Deletes the master key
def delete_key():
    deleted_key = client.begin_delete_key(MASTER_KEY)
    # block until deletion is complete
    deleted_key.wait()
    return deleted_key

# Disables key
def disable_key():
    client.update_key_properties(MASTER_KEY, enabled=False)

#-----------------------------------------------------------------------
# Cryptographic operations helper functions
#-----------------------------------------------------------------------

# Initializes Crytpgraphy Client
def init_crypto_client():
    rsa_key = retrieve_master_key()
    crypto_client = crypto.CryptographyClient(rsa_key, credential=credential)
    return crypto_client

# Initialize AES encryption algorithm
# true = encryption
# false = decryption 
def init_aes_context(aes_key: bytes, iv: bytes, mode: bool):
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv))
    if mode:
        return cipher.encryptor()
    else:
        return cipher.decryptor()

def unpack_payload(payload: dict):
    encrypted_aes_key = base64.b64decode(payload["encrypted_aes_key"])
    iv = base64.b64decode(payload["iv"])
    ciphertext = base64.b64decode(payload["ciphertext"])
    return encrypted_aes_key, iv, ciphertext

# AES (CBC mode) requires input to be a multiple of 128 bits
def pad_data(data: bytes):
    padder = padding.PKCS7(BLOCK_BIT_SIZE).padder()
    padded_data = padder.update(data) + padder.finalize()
    return padded_data

def unpad_data(padded_data: bytes):
    unpadder = padding.PKCS7(BLOCK_BIT_SIZE).unpadder()
    data = unpadder.update(padded_data) + unpadder.finalize()
    return data

#-----------------------------------------------------------------------
# Cryptographic operations
#-----------------------------------------------------------------------

# TODO: Decide if we want to give everythign to the user (ciphertext, encrypted key, & iv)
# TODO: Maybe have a button asking user if they want to store this data in our database
# TODO: If yes, we should encrypt them again with a master key
def encrypt_data(file_bytes: bytes):
    # Generating random AES key
    aes_key = os.urandom(AES_BYTE_SIZE)
    # Random salt for encryption
    iv = os.urandom(IV_BYTE_SIZE)

    padded_data = pad_data(file_bytes)

    # Encryting clients data with AES key
    aes_encryptor = init_aes_context(aes_key, iv, True)
    cipher_text = aes_encryptor.update(padded_data) + aes_encryptor.finalize()

    # Encrypting the AES key with RSA key
    crypto_client = init_crypto_client()
    encrypted_aes_key = crypto_client.encrypt(crypto.EncryptionAlgorithm.rsa_oaep, aes_key).ciphertext
    
    # TODO: add a check here to see if client wants us to store a backup in our database
    # Client needs to keep encrypted key, IV, and ciphertext safe to decrypt their data
    payload = {
        "encrypted_aes_key": base64.b64encode(encrypted_aes_key).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ciphertext": base64.b64encode(cipher_text).decode()
    }

    return payload

def decrypt_data(payload: dict):
    encrypted_aes_key, iv, ciphertext = unpack_payload(payload)

    # Decrypting AES key with RSA key
    crypto_client = init_crypto_client()
    aes_key = crypto_client.decrypt(crypto.EncryptionAlgorithm.rsa_oaep, encrypted_aes_key).plaintext

    # Decrypt ciphertext with AES key
    aes_decryptor = init_aes_context(aes_key, iv, False)
    padded_data = aes_decryptor.update(ciphertext) + aes_decryptor.finalize()

    data = unpad_data(padded_data)

    return data
