import json
import os
from web3 import Web3
from dotenv import load_dotenv

# -------------------- Load environment --------------------
load_dotenv()
RPC_URL = os.getenv("RPC_URL")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# Connect to blockchain
w3 = Web3(Web3.HTTPProvider(RPC_URL))
if not w3.is_connected():
    raise ConnectionError("❌ Failed to connect to blockchain. Check RPC_URL.")

# Create account object
acct = w3.eth.account.from_key(PRIVATE_KEY)
print("Connected ")
print("Account:", acct.address)
print("Current block:", w3.eth.block_number)
print("Chain ID:", w3.eth.chain_id)

# -------------------- Load contract ABI + Bytecode --------------------
abi_path = os.path.join(os.path.dirname(__file__), "../abi/IndiCoin.json")
bytecode_path = os.path.join(os.path.dirname(__file__), "../bytecode/IndiCoin.bin")

with open(abi_path) as f:
    abi = json.load(f)
with open(bytecode_path) as f:
    bytecode = f.read()

IndiCoin = w3.eth.contract(abi=abi, bytecode=bytecode)

# -------------------- Build transaction --------------------
initial_supply = 1_000_000  # example: 1 million tokens

nonce = w3.eth.get_transaction_count(acct.address)

# Estimate gas dynamically
# Pick your green fund address (right now, using deployer's address)
green_fund_address = acct.address  

try:
    estimated_gas = IndiCoin.constructor(green_fund_address).estimate_gas({"from": acct.address})
    print("Estimated gas:", estimated_gas)
except Exception as e:
    print(" Gas estimation failed, using default 5,000,000")
    estimated_gas = 5_000_000

tx = IndiCoin.constructor(green_fund_address).build_transaction({
    "from": acct.address,
    "nonce": nonce,
    "gas": estimated_gas,
    "gasPrice": w3.eth.gas_price,
})



# -------------------- Sign & send transaction --------------------
signed_tx = acct.sign_transaction(tx)
try:
    tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
    print("Transaction sent. Waiting for confirmation...")
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
except Exception as e:
    raise RuntimeError(" Deployment failed:", e)

# -------------------- Deployment success --------------------
contract_address = receipt.contractAddress
print(" Contract deployed at:", contract_address)
print("Block Number:", receipt.blockNumber)
print("Gas Used:", receipt.gasUsed)

# Save deployed address to file
address_file = os.path.join(os.path.dirname(__file__), "deployed_address.txt")
with open(address_file, "w") as f:
    f.write(contract_address)
#print(" Deployed address saved to:", address_file)
