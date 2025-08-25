#!/usr/bin/env python3
"""
IndiCoin Contract Testing Script
Role 1: Smart Contract Developer - Unit Tests
"""

import json
import os
from pathlib import Path
from web3 import Web3
from eth_account import Account
import time

class IndiCoinTester:
    def __init__(self):
        # Setup local blockchain (Ganache CLI or similar)
        self.w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
        
        # Create test accounts
        self.owner_account = Account.create()
        self.user1_account = Account.create()
        self.user2_account = Account.create()
        self.green_fund_account = Account.create()
        
        # Load contract artifacts
        self.load_contract_artifacts()
        
        # Test results
        self.test_results = []
        
    def load_contract_artifacts(self):
        """Load compiled contract ABI and bytecode"""
        build_dir = Path("build")
        
        # Load ABI
        with open(build_dir / "IndiCoin_abi.json", "r") as f:
            self.abi = json.load(f)
        
        # Load bytecode
        with open(build_dir / "IndiCoin_bytecode.txt", "r") as f:
            self.bytecode = f.read().strip()
            
        print("📋 Contract artifacts loaded")
    
    def setup_local_blockchain(self):
        """Setup local test environment"""
        print("🔧 Setting up local test blockchain...")
        
        # Check if connected to local blockchain
        if not self.w3.is_connected():
            print("❌ Cannot connect to local blockchain")
            print("💡 Start Ganache CLI: ganache-cli --deterministic --accounts 10 --host 0.0.0.0")
            return False
        
        # Use pre-funded accounts from Ganache
        accounts = self.w3.eth.accounts
        if len(accounts) < 4:
            print("❌ Need at least 4 accounts")
            return False
            
        self.owner_address = accounts[0]
        self.user1_address = accounts[1] 
        self.user2_address = accounts[2]
        self.green_fund_address = accounts[3]
        
        print(f"✅ Test accounts ready:")
        print(f"   Owner: {self.owner_address}")
        print(f"   User1: {self.user1_address}")
        print(f"   User2: {self.user2_address}")
        print(f"   Green Fund: {self.green_fund_address}")
        
        return True
    
    def deploy_contract(self):
        """Deploy IndiCoin contract for testing"""
        print("🚀 Deploying IndiCoin contract...")
        
        try:
            # Create contract instance
            contract = self.w3.eth.contract(abi=self.abi, bytecode=self.bytecode)
            
            # Deploy with green fund address as constructor parameter
            tx_hash = contract.constructor(self.green_fund_address).transact({
                'from': self.owner_address,
                'gas': 3000000
            })
            
            # Wait for deployment
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
            
            self.contract = self.w3.eth.contract(
                address=tx_receipt.contractAddress,
                abi=self.abi
            )
            
            print(f"✅ Contract deployed at: {tx_receipt.contractAddress}")
            return True
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False
    
    def run_test(self, test_name, test_func):
        """Run a single test and record results"""
        print(f"\n🧪 Testing: {test_name}")
        try:
            result = test_func()
            if result:
                print(f"✅ {test_name} PASSED")
                self.test_results.append((test_name, "PASSED", None))
            else:
                print(f"❌ {test_name} FAILED")
                self.test_results.append((test_name, "FAILED", "Test returned False"))
        except Exception as e:
            print(f"💥 {test_name} ERROR: {e}")
            self.test_results.append((test_name, "ERROR", str(e)))
    
    def test_basic_info(self):
        """Test basic contract information"""
        name = self.contract.functions.name().call()
        symbol = self.contract.functions.symbol().call()
        decimals = self.contract.functions.decimals().call()
        owner = self.contract.functions.owner().call()
        
        expected_results = [
            (name == "IndiCoin", f"Name: expected 'IndiCoin', got '{name}'"),
            (symbol == "INDI", f"Symbol: expected 'INDI', got '{symbol}'"),
            (decimals == 18, f"Decimals: expected 18, got {decimals}"),
            (owner.lower() == self.owner_address.lower(), f"Owner mismatch")
        ]
        
        for result, error_msg in expected_results:
            if not result:
                print(f"   ❌ {error_msg}")
                return False
        
        print(f"   ✅ Name: {name}, Symbol: {symbol}, Decimals: {decimals}")
        return True
    
    def test_mint_by_owner(self):
        """Test minting by owner (should succeed)"""
        mint_amount = self.w3.to_wei(1000, 'ether')  # 1000 tokens
        
        # Check initial balance
        initial_balance = self.contract.functions.balanceOf(self.user1_address).call()
        initial_supply = self.contract.functions.totalSupply().call()
        
        # Mint tokens
        tx_hash = self.contract.functions.mint(self.user1_address, mint_amount).transact({
            'from': self.owner_address
        })
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Check final balance
        final_balance = self.contract.functions.balanceOf(self.user1_address).call()
        final_supply = self.contract.functions.totalSupply().call()
        
        balance_increased = (final_balance - initial_balance) == mint_amount
        supply_increased = (final_supply - initial_supply) == mint_amount
        
        if balance_increased and supply_increased:
            print(f"   ✅ Minted {self.w3.from_wei(mint_amount, 'ether')} tokens")
            return True
        else:
            print(f"   ❌ Mint failed - balance: {balance_increased}, supply: {supply_increased}")
            return False
    
    def test_mint_by_non_owner(self):
        """Test minting by non-owner (should fail)"""
        mint_amount = self.w3.to_wei(100, 'ether')
        
        try:
            tx_hash = self.contract.functions.mint(self.user2_address, mint_amount).transact({
                'from': self.user1_address  # Not the owner
            })
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print("   ❌ Non-owner mint should have failed but succeeded")
            return False
        except Exception as e:
            if "Not authorized" in str(e) or "revert" in str(e):
                print("   ✅ Non-owner mint correctly rejected")
                return True
            else:
                print(f"   ❌ Unexpected error: {e}")
                return False
    
    def test_set_outflow_cap(self):
        """Test setting outflow cap (AI/ML integration)"""
        new_cap = self.w3.to_wei(500, 'ether')  # 500 tokens
        
        # Set new cap
        tx_hash = self.contract.functions.setOutflowCap(new_cap).transact({
            'from': self.owner_address
        })
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Verify cap was set
        current_cap = self.contract.functions.outflowCap().call()
        
        if current_cap == new_cap:
            print(f"   ✅ Outflow cap set to {self.w3.from_wei(new_cap, 'ether')} tokens")
            return True
        else:
            print(f"   ❌ Cap mismatch: expected {new_cap}, got {current_cap}")
            return False
    
    def test_burn_within_cap(self):
        """Test burning within outflow cap (should succeed)"""
        burn_amount = self.w3.to_wei(100, 'ether')  # 100 tokens (within 500 cap)
        
        # Check user1 has enough balance
        user_balance = self.contract.functions.balanceOf(self.user1_address).call()
        if user_balance < burn_amount:
            print(f"   ❌ Insufficient balance for test: {self.w3.from_wei(user_balance, 'ether')}")
            return False
        
        initial_supply = self.contract.functions.totalSupply().call()
        
        # Burn tokens
        tx_hash = self.contract.functions.burn(burn_amount).transact({
            'from': self.user1_address
        })
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Verify burn
        final_balance = self.contract.functions.balanceOf(self.user1_address).call()
        final_supply = self.contract.functions.totalSupply().call()
        
        balance_decreased = (user_balance - final_balance) == burn_amount
        supply_decreased = (initial_supply - final_supply) == burn_amount
        
        if balance_decreased and supply_decreased:
            print(f"   ✅ Burned {self.w3.from_wei(burn_amount, 'ether')} tokens within cap")
            return True
        else:
            print(f"   ❌ Burn failed - balance: {balance_decreased}, supply: {supply_decreased}")
            return False
    
    def test_burn_beyond_cap(self):
        """Test burning beyond outflow cap (should fail)"""
        # Try to burn more than the remaining cap
        large_burn = self.w3.to_wei(600, 'ether')  # 600 tokens (beyond 500 cap)
        
        try:
            tx_hash = self.contract.functions.burn(large_burn).transact({
                'from': self.user1_address
            })
            self.w3.eth.wait_for_transaction_receipt(tx_hash)
            print("   ❌ Burn beyond cap should have failed but succeeded")
            return False
        except Exception as e:
            if "Exceeds outflow cap" in str(e) or "revert" in str(e):
                print("   ✅ Burn beyond cap correctly rejected")
                return True
            else:
                print(f"   ❌ Unexpected error: {e}")
                return False
    
    def test_green_fund_transfer(self):
        """Test green fund contribution on transfers"""
        transfer_amount = self.w3.to_wei(100, 'ether')  # 100 tokens
        
        # Check initial balances
        sender_initial = self.contract.functions.balanceOf(self.user1_address).call()
        receiver_initial = self.contract.functions.balanceOf(self.user2_address).call()
        green_fund_initial = self.contract.functions.balanceOf(self.green_fund_address).call()
        
        if sender_initial < transfer_amount:
            print(f"   ❌ Insufficient sender balance: {self.w3.from_wei(sender_initial, 'ether')}")
            return False
        
        # Make transfer
        tx_hash = self.contract.functions.transfer(self.user2_address, transfer_amount).transact({
            'from': self.user1_address
        })
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Check final balances
        sender_final = self.contract.functions.balanceOf(self.user1_address).call()
        receiver_final = self.contract.functions.balanceOf(self.user2_address).call()
        green_fund_final = self.contract.functions.balanceOf(self.green_fund_address).call()
        
        # Calculate expected values (1% to green fund)
        green_fund_fee = transfer_amount // 100  # 1%
        actual_transfer = transfer_amount - green_fund_fee
        
        sender_decreased = (sender_initial - sender_final) == transfer_amount
        receiver_increased = (receiver_final - receiver_initial) == actual_transfer
        green_fund_increased = (green_fund_final - green_fund_initial) == green_fund_fee
        
        if sender_decreased and receiver_increased and green_fund_increased:
            print(f"   ✅ Transfer with 1% green fund fee: {self.w3.from_wei(green_fund_fee, 'ether')} INDI")
            return True
        else:
            print(f"   ❌ Transfer failed - sender: {sender_decreased}, receiver: {receiver_increased}, green: {green_fund_increased}")
            return False
    
    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🧪 IndiCoin Contract Test Suite")
        print("=" * 50)
        
        # Setup
        if not self.setup_local_blockchain():
            return False
            
        if not self.deploy_contract():
            return False
        
        # Run tests
        tests = [
            ("Basic Contract Info", self.test_basic_info),
            ("Mint by Owner", self.test_mint_by_owner),
            ("Mint by Non-Owner (should fail)", self.test_mint_by_non_owner),
            ("Set Outflow Cap", self.test_set_outflow_cap),
            ("Burn Within Cap", self.test_burn_within_cap),
            ("Burn Beyond Cap (should fail)", self.test_burn_beyond_cap),
            ("Green Fund Transfer", self.test_green_fund_transfer),
        ]
        
        for test_name, test_func in tests:
            self.run_test(test_name, test_func)
        
        # Summary
        self.print_test_summary()
        
        return all(result[1] == "PASSED" for result in self.test_results)
    
    def print_test_summary(self):
        """Print test results summary"""
        print("\n📊 Test Results Summary")
        print("=" * 50)
        
        passed = sum(1 for _, status, _ in self.test_results if status == "PASSED")
        failed = sum(1 for _, status, _ in self.test_results if status == "FAILED")
        errors = sum(1 for _, status, _ in self.test_results if status == "ERROR")
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"💥 Errors: {errors}")
        print(f"📈 Success Rate: {passed}/{len(self.test_results)} ({passed/len(self.test_results)*100:.1f}%)")
        
        # Show failed tests
        if failed > 0 or errors > 0:
            print("\n❌ Failed/Error Tests:")
            for test_name, status, error in self.test_results:
                if status in ["FAILED", "ERROR"]:
                    print(f"   - {test_name}: {status}")
                    if error:
                        print(f"     Error: {error}")

def main():
    """Main testing workflow"""
    try:
        tester = IndiCoinTester()
        success = tester.run_all_tests()
        
        if success:
            print("\n🎉 ALL TESTS PASSED!")
            print("✅ IndiCoin contract is ready for deployment!")
        else:
            print("\n⚠️  Some tests failed. Review and fix issues.")
            
        return success
        
    except FileNotFoundError:
        print("❌ Contract artifacts not found. Run compile_contract.py first!")
        return False
    except Exception as e:
        print(f"💥 Testing failed: {e}")
        print("💡 Make sure Ganache CLI is running: ganache-cli --deterministic")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)