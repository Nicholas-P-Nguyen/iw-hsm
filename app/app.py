from azure.identity import DefaultAzureCredential
from azure.keyvault.keys import KeyClient
import os

VAULT_URL = os.environ["https://COSIW11.vault.azure.net/"]
credential = DefaultAzureCredential()
client = KeyClient(vault_url=VAULT_URL, credential=credential)

