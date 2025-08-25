# app/burn_tokens.py
import json, os
from web3 import Web3
from dotenv import load_dotenv
import subprocess

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



def burn(amount: int):
    try:
        nonce = w3.eth.get_transaction_count(acct.address)
        tx = contract.functions.burn(amount).build_transaction({
            "from": acct.address,
            "nonce": nonce,
            "gas": 200000,
            "gasPrice": w3.eth.gas_price,
        })

        signed_tx = acct.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status == 1:
            print(f"✅ Successfully burned {amount} tokens")
            print("Transaction Hash:", tx_hash.hex())
        else:
            print("❌ Burn transaction failed")

    except Exception as e:
        print("❌ Error while burning tokens:", e)


if __name__ == "__main__":
    import sys
    import subprocess

    # --- NEW: check if burn.py is called with a final confirmed amount ---
    if len(sys.argv) == 2:
        amount_to_burn = int(float(sys.argv[1]))
        burn(amount_to_burn)

    else:
        # original user input flow
        currency = input("Enter currency type: ")
        amount_to_burn = int(float(input("Enter amount to burn: ")))  # ensures integer type

        if currency.strip().lower() == "rupees":
            burn(amount_to_burn)
        else:
            try:
                # Run AI script which will handle sending output to set.py
                venv_python = sys.executable
                subprocess.run([venv_python, "app/ai.py", str(amount_to_burn)], check=True)

            except Exception as e:
                print("❌ Error while running AI script:", e)
