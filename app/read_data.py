# app/read_data.py
import json, os, sys
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to Web3
RPC_URL = os.getenv("RPC_URL")
w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    print("❌ Failed to connect to RPC. Check your RPC_URL in .env")
    sys.exit(1)

# Load ABI
ABI_PATH = os.path.join(os.path.dirname(__file__), "..", "abi", "IndiCoin.json")
try:
    with open(ABI_PATH) as f:
        abi = json.load(f)
except FileNotFoundError:
    print(f"❌ ABI file not found at {ABI_PATH}")
    sys.exit(1)

# Load deployed contract address
ADDRESS_PATH = os.path.join(os.path.dirname(__file__), "deployed_address.txt")
try:
    with open(ADDRESS_PATH, "r") as f:
        contract_address = Web3.to_checksum_address(f.read().strip())
except FileNotFoundError:
    print(f"❌ deployed_address.txt not found at {ADDRESS_PATH}")
    sys.exit(1)

contract = w3.eth.contract(address=contract_address, abi=abi)

# Verify contract exists
if w3.eth.get_code(contract_address) == b'':
    print(f"❌ No contract found at {contract_address} on {RPC_URL}")
    sys.exit(1)

def read_data(wallet_address: str):
    try:
        wallet_address = Web3.to_checksum_address(wallet_address)

        balance = contract.functions.balanceOf(wallet_address).call()
        total_supply = contract.functions.totalSupply().call()
        outflow_cap = contract.functions.outflowCap().call()

        print("📊 On-chain Data")
        print(f"   Balance of {wallet_address}: {balance} IND")
        print(f"   Total Supply: {total_supply} IND")
        print(f"   Outflow Cap: {outflow_cap}")

    except Exception as e:
        print("❌ Error reading data:", e)

# Example usage
if __name__ == "__main__":
    # CLI: python app/read_data.py 0xSomeWallet
    if len(sys.argv) > 1:
        wallet_to_check = sys.argv[1]
    else:
        wallet_to_check = os.getenv("ACCOUNT_ADDRESS")  # fallback

    if not wallet_to_check:
        print("❌ No wallet address provided (CLI arg or ACCOUNT_ADDRESS in .env required)")
        sys.exit(1)

    read_data(wallet_to_check)
