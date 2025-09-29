#!/usr/bin/env python3
"""
Local Deployment Script for IndiCoin
Role 1: Smart Contract Developer - Deployment Dry-Run
"""

import json
import time
from pathlib import Path
from web3 import Web3
from eth_account import Account

class IndiCoinDeployer:
    def __init__(self):
        # Connect to local blockchain
        self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
        
        # Load contract artifacts
        self.load_artifacts()
        
        # Setup accounts
        self.setup_accounts()
    
    def load_artifacts(self):
        """Load compiled contract artifacts"""
        build_dir = Path("build")
        
        # Load ABI
        with open(build_dir / "IndiCoin_abi.json", "r") as f:
            self.abi = json.load(f)
        
        # Load bytecode
        with open(build_dir / "IndiCoin_bytecode.txt", "r") as f:
            self.bytecode = f.read().strip()
        
        print("📋 Contract artifacts loaded")
    
    def setup_accounts(self):
        """Setup deployment accounts"""
        if not self.w3.is_connected():
            raise ConnectionError("Cannot connect to local blockchain")
        
        accounts = self.w3.eth.accounts
        if len(accounts) < 2:
            raise ValueError("Need at least 2 accounts for deployment")
        
        self.deployer = accounts[0]
        self.green_fund = accounts[1]
        
        print(f"🔑 Deployer: {self.deployer}")
        print(f"🌱 Green Fund: {self.green_fund}")
    
    def deploy_contract(self):
        """Deploy IndiCoin contract"""
        print("🚀 Deploying IndiCoin contract...")
        
        try:
            # Create contract instance
            contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
            
            # Estimate gas
            gas_estimate = contract.constructor(self.green_fund).estimate_gas({
                'from': self.deployer
            })
            
            print(f"⛽ Estimated gas: {gas_estimate:,}")
            
            # Deploy contract
            tx_hash = contract.constructor(self.green_fund).transact({
                'from': self.deployer,
                'gas': gas_estimate + 100000  # Add buffer
            })
            
            print(f"📝 Transaction hash: {tx_hash.hex()}")
            print("⏳ Waiting for deployment...")
            
            # Wait for transaction receipt
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            if tx_receipt.status != 1:
                raise Exception("Deployment transaction failed")
            
            # Create contract instance
            self.contract = self.w3.eth.contract(
                address=tx_receipt.contractAddress,
                abi=self.abi
            )
            
            print(f"✅ Contract deployed at: {tx_receipt.contractAddress}")
            print(f"⛽ Gas used: {tx_receipt.gasUsed:,}")
            
            return tx_receipt.contractAddress
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            raise
    
    def verify_deployment(self):
        """Verify contract was deployed correctly"""
        print("\n🔍 Verifying deployment...")
        
        try:
            # Test basic contract calls
            name = self.contract.functions.name().call()
            symbol = self.contract.functions.symbol().call()
            decimals = self.contract.functions.decimals().call()
            owner = self.contract.functions.owner().call()
            total_supply = self.contract.functions.totalSupply().call()
            outflow_cap = self.contract.functions.outflowCap().call()
            
            print(f"📊 Contract Details:")
            print(f"   Name: {name}")
            print(f"   Symbol: {symbol}")
            print(f"   Decimals: {decimals}")
            print(f"   Owner: {owner}")
            print(f"   Total Supply: {self.w3.from_wei(total_supply, 'ether')} INDI")
            
            # 2. Test transfer with green fund
            transfer_amount = self.w3.to_wei(100, 'ether')  # 100 INDI
            print(f"\n💸 Transferring {self.w3.from_wei(transfer_amount, 'ether')} INDI to Green Fund...")
            
            initial_green_balance = self.contract.functions.balanceOf(self.green_fund).call()
            
            tx_hash = self.contract.functions.transfer(self.green_fund, transfer_amount).transact({
                'from': self.deployer,
                'gas': 200000
            })
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            final_green_balance = self.contract.functions.balanceOf(self.green_fund).call()
            green_fund_fee = (final_green_balance - initial_green_balance)
            actual_transfer = transfer_amount - (transfer_amount // 100)  # 1% fee
            
            print(f"   Green Fund received: {self.w3.from_wei(green_fund_fee, 'ether')} INDI")
            print(f"   Actual transfer: {self.w3.from_wei(actual_transfer, 'ether')} INDI")
            
            # 3. Test outflow cap setting
            new_cap = self.w3.to_wei(500, 'ether')  # 500 INDI
            print(f"\n🔒 Setting outflow cap to {self.w3.from_wei(new_cap, 'ether')} INDI...")
            
            tx_hash = self.contract.functions.setOutflowCap(new_cap).transact({
                'from': self.deployer,
                'gas': 100000
            })
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            current_cap = self.contract.functions.outflowCap().call()
            print(f"   Outflow cap set to: {self.w3.from_wei(current_cap, 'ether')} INDI")
            
            # 4. Test burning within cap
            burn_amount = self.w3.to_wei(50, 'ether')  # 50 INDI (within 500 cap)
            print(f"\n🔥 Burning {self.w3.from_wei(burn_amount, 'ether')} INDI tokens...")
            
            initial_balance = self.contract.functions.balanceOf(self.deployer).call()
            initial_supply = self.contract.functions.totalSupply().call()
            
            tx_hash = self.contract.functions.burn(burn_amount).transact({
                'from': self.deployer,
                'gas': 200000
            })
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            final_balance = self.contract.functions.balanceOf(self.deployer).call()
            final_supply = self.contract.functions.totalSupply().call()
            
            print(f"   Tokens burned: {self.w3.from_wei(initial_balance - final_balance, 'ether')} INDI")
            print(f"   New total supply: {self.w3.from_wei(final_supply, 'ether')} INDI")
            
            print("✅ Functionality demonstration completed!")
            return True
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            return False
    
    def generate_deployment_summary(self, contract_address):
        """Generate deployment summary for Python teammate"""
        summary = {
            "contract_address": contract_address,
            "deployer": self.deployer,
            "green_fund": self.green_fund,
            "network": "localhost:8545",
            "gas_used": "~3M gas",
            "timestamp": int(time.time()),
            "abi_file": "build/IndiCoin_abi.json",
            "bytecode_file": "build/IndiCoin_bytecode.txt"
        }
        
        # Save summary to file
        with open("build/deployment_summary.json", "w") as f:
            json.dump(summary, f, indent=2)
        
        print("\n📄 Deployment Summary:")
        print(f"   Contract Address: {contract_address}")
        print(f"   Network: localhost:8545")
        print(f"   Deployer: {self.deployer}")
        print(f"   Green Fund: {self.green_fund}")
        print("   Files for Python teammate:")
        print("     - build/IndiCoin_abi.json")
        print("     - build/IndiCoin_bytecode.txt")
        print("     - build/deployment_summary.json")
        
        return summary

def main():
    """Main deployment workflow"""
    print("🚀 IndiCoin Local Deployment")
    print("=" * 50)
    
    try:
        # Initialize deployer
        deployer = IndiCoinDeployer()
        
        # Deploy contract
        contract_address = deployer.deploy_contract()
        
        # Verify deployment
        if not deployer.verify_deployment():
            print("❌ Deployment verification failed")
            return False
        
        # Demonstrate functionality
        if not deployer.demo_functionality():
            print("❌ Functionality demo failed")
            return False
        
        # Generate summary
        deployer.generate_deployment_summary(contract_address)
        
        print("\n🎉 SUCCESS: IndiCoin deployed and tested locally!")
        print("\n📦 Ready for Python teammate:")
        print("   All artifacts are in the 'build/' directory")
        print("   Contract is deployed and functional")
        
        return True
        
    except FileNotFoundError:
        print("❌ Contract artifacts not found. Run compile_contract.py first!")
        return False
    except ConnectionError:
        print("❌ Cannot connect to blockchain. Start Ganache CLI:")
        print("   ganache-cli --deterministic --accounts 10 --host 0.0.0.0")
        return False
    except Exception as e:
        print(f"💥 Deployment failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)