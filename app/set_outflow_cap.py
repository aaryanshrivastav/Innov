# app/set_outflow_cap.py
import json, os
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to Web3
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
acct = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

# Load ABI
abi_path = os.path.join(os.path.dirname(__file__), "../abi/IndiCoin.json")
with open(abi_path) as f:
    abi = json.load(f)

# Load deployed contract address
address_file = os.path.join(os.path.dirname(__file__), "deployed_address.txt")
with open(address_file, "r") as f:
    contract_address = f.read().strip()

contract = w3.eth.contract(address=contract_address, abi=abi)

def set_cap(new_cap: int):
    try:
        nonce = w3.eth.get_transaction_count(acct.address)
        tx = contract.functions.setOutflowCap(new_cap).build_transaction({
            "from": acct.address,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
        })

        signed_tx = acct.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            print(f"✅ Outflow cap successfully set to {new_cap}")
            print("Transaction Hash:", tx_hash.hex())
        else:
            print("❌ Setting outflow cap failed")

    except Exception as e:
        print("❌ Error while setting outflow cap:", e)

# Example usage
if __name__ == "__main__":
    new_cap_value = 500  # Replace with the desired cap
    set_cap(new_cap_value)
