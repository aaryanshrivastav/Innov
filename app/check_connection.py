from web3 import Web3
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Get RPC URL
rpc_url = os.getenv("RPC_URL")
w3 = Web3(Web3.HTTPProvider(rpc_url))

print("Connected:", w3.is_connected())
if w3.is_connected():
    print("Current Block:", w3.eth.block_number)
