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

if __name__ == "__main__":
    import sys
    try:
        if len(sys.argv) != 2:
            print("❌ Missing input value from AI")
            sys.exit(1)

        new_value = int(float(sys.argv[1]))
        print(f"AI suggested value: {new_value}")

        confirm = input("Do you confirm this amount? (yes/no): ").strip().lower()
        if confirm == "yes":
            # Call burn.py with confirmed value
            import subprocess
            import sys
            venv_python = sys.executable
            subprocess.run([venv_python, "app/burn_tokens.py", str(new_value)], check=True)


        else:
            print("❌ User declined. Exiting gracefully.")
            sys.exit(0)

    except Exception as e:
        print("❌ Error in set.py:", e)
        sys.exit(1)
