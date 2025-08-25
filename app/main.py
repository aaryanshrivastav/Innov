import os
from web3 import Web3
from dotenv import load_dotenv

# load secrets from .env
load_dotenv()

RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
ACCOUNT_ADDRESS = os.getenv("ACCOUNT_ADDRESS")

# connect to blockchain
web3 = Web3(Web3.HTTPProvider(RPC_URL))

print("Connected:", web3.is_connected())
print("Current block:", web3.eth.block_number)
print("Account:", ACCOUNT_ADDRESS)
