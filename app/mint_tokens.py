# app/mint_tokens.py
import json, os
from web3 import Web3
from web3.middleware.proof_of_authority import ExtraDataToPOAMiddleware
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect to Web3
w3 = Web3(Web3.HTTPProvider(os.getenv("RPC_URL")))
w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

# Load account
acct = w3.eth.account.from_key(os.getenv("PRIVATE_KEY"))

# Load ABI
abi_path = os.path.join(os.path.dirname(__file__), "../abi/IndiCoin.json")
with open(abi_path) as f:
    abi = json.load(f)

# Load contract address from file
address_file = os.path.join(os.path.dirname(__file__), "deployed_address.txt")
with open(address_file, "r") as f:
    contract_address = f.read().strip()

contract = w3.eth.contract(address=contract_address, abi=abi)

def mint(to: str, amount: int):
    try:
        nonce = w3.eth.get_transaction_count(acct.address)
        tx = contract.functions.mint(to, amount).build_transaction({
            "from": acct.address,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
        })

        signed_tx = w3.eth.account.sign_transaction(tx, private_key=os.getenv("PRIVATE_KEY"))
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            print(f"✅ Successfully minted {amount} tokens to {to}")
            print("Transaction Hash:", tx_hash.hex())
        else:
            print("❌ Minting failed")

    except Exception as e:
        print("❌ Error while minting:", e)

# Example usage
if __name__ == "__main__":
    recipient_address = "0x99bf0d3951523fe229232333F11a803c4023b079"
    amount_to_mint = 1000
    mint(recipient_address, amount_to_mint)
