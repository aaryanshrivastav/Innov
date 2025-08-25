import json
from web3 import Web3
from dotenv import load_dotenv
import os

load_dotenv()

# Paths
ADDRESS_PATH = "app/deployed_address.txt"
ABI_PATH = "abi/IndiCoin.json"

# RPC from env
RPC_URL = os.getenv("RPC_URL")

# Read contract address
try:
    with open(ADDRESS_PATH, "r") as f:
        CONTRACT_ADDRESS = f.read().strip()
except FileNotFoundError:
    print("❌ deployed_address.txt not found. Deploy the contract first.")
    exit(1)

# Read ABI
try:
    with open(ABI_PATH, "r") as f:
        abi = json.load(f)
except FileNotFoundError:
    print("❌ ABI file not found at", ABI_PATH)
    exit(1)

# Connect Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))
print("RPC_URL:", RPC_URL)
print("Connected:", w3.is_connected())

if w3.is_connected():
    try:
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACT_ADDRESS),
            abi=abi
        )
        print("✅ Contract found at:", contract.address)
    except Exception as e:
        print("❌ Error loading contract:", e)
