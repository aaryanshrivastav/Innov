#!/usr/bin/env python3
"""
Comprehensive PyTest Suite for IndiCoin
Fixed version with proper error handling and transaction management
"""

import pytest
import json
import os
from pathlib import Path
from web3 import Web3
from eth_account import Account

@pytest.fixture(scope="session")
def w3():
    """Web3 connection fixture"""
    web3_instance = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    if not web3_instance.is_connected():
        pytest.skip("Local blockchain not available. Start with: ganache-cli --deterministic")
    return web3_instance

@pytest.fixture(scope="session") 
def accounts(w3):
    """Test accounts fixture"""
    accounts_list = w3.eth.accounts
    if len(accounts_list) < 4:
        pytest.skip("Need at least 4 test accounts")
    
    return {
        'owner': accounts_list[0],
        'user1': accounts_list[1], 
        'user2': accounts_list[2],
        'green_fund': accounts_list[3]
    }

@pytest.fixture(scope="session")
def contract_artifacts():
    """Load compiled contract artifacts"""
    build_dir = Path("build")
    
    # Load ABI
    abi_file = build_dir / "IndiCoin_abi.json"
    if not abi_file.exists():
        pytest.skip("Contract not compiled. Run: python scripts/compile_contract.py")
    
    with open(abi_file, "r") as f:
        abi = json.load(f)
    
    # Load bytecode
    bytecode_file = build_dir / "IndiCoin_bytecode.txt"
    if not bytecode_file.exists():
        pytest.skip("Bytecode file not found")
        
    with open(bytecode_file, "r") as f:
        bytecode = f.read().strip()
        if not bytecode.startswith('0x'):
            bytecode = '0x' + bytecode
    
    return {"abi": abi, "bytecode": bytecode}

@pytest.fixture(scope="session")
def deployed_contract(w3, accounts, contract_artifacts):
    """Deploy contract for testing"""
    # Create contract instance
    contract = w3.eth.contract(
        abi=contract_artifacts["abi"], 
        bytecode=contract_artifacts["bytecode"]
    )
    
    # Deploy with green fund address
    tx_hash = contract.constructor(accounts['green_fund']).transact({
        'from': accounts['owner'],
        'gas': 3000000
    })
    
    # Wait for deployment
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    
    if tx_receipt.status != 1:
        pytest.fail(f"Contract deployment failed: {tx_receipt}")
    
    # Return deployed contract instance
    return w3.eth.contract(
        address=tx_receipt.contractAddress,
        abi=contract_artifacts["abi"]
    )

class TestIndiCoinBasics:
    """Test basic contract functionality"""
    
    def test_contract_deployment(self, deployed_contract, accounts):
        """Test contract was deployed correctly"""
        assert deployed_contract.address is not None
        assert len(deployed_contract.address) == 42  # Ethereum address format
        
        # Check owner is set correctly
        owner = deployed_contract.functions.owner().call()
        assert owner.lower() == accounts['owner'].lower()
    
    def test_token_info(self, deployed_contract):
        """Test token basic information"""
        assert deployed_contract.functions.name().call() == "IndiCoin"
        assert deployed_contract.functions.symbol().call() == "INDI"
        assert deployed_contract.functions.decimals().call() == 18
    
    def test_initial_state(self, deployed_contract, accounts):
        """Test initial contract state"""
        # Total supply should be 0
        assert deployed_contract.functions.totalSupply().call() == 0
        
        # All balances should be 0
        assert deployed_contract.functions.balanceOf(accounts['owner']).call() == 0
        assert deployed_contract.functions.balanceOf(accounts['user1']).call() == 0
        
        # Outflow cap should be set to default
        outflow_cap = deployed_contract.functions.outflowCap().call()
        expected_cap = Web3.to_wei(1000000, 'ether')  # 1M tokens default
        assert outflow_cap == expected_cap
        
        # Contract should not be paused
        assert deployed_contract.functions.emergencyPause().call() == False

class TestMinting:
    """Test token minting functionality"""
    
    def test_mint_by_owner_success(self, w3, deployed_contract, accounts):
        """Test successful minting by owner"""
        mint_amount = Web3.to_wei(1000, 'ether')  # 1000 tokens
        
        # Get initial state
        initial_balance = deployed_contract.functions.balanceOf(accounts['user1']).call()
        initial_supply = deployed_contract.functions.totalSupply().call()
        
        # Mint tokens
        tx_hash = deployed_contract.functions.mint(accounts['user1'], mint_amount).transact({
            'from': accounts['owner'],
            'gas': 200000
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Check transaction succeeded
        assert tx_receipt.status == 1, f"Transaction failed: {tx_receipt}"
        
        # Verify results
        final_balance = deployed_contract.functions.balanceOf(accounts['user1']).call()
        final_supply = deployed_contract.functions.totalSupply().call()
        
        assert final_balance - initial_balance == mint_amount
        assert final_supply - initial_supply == mint_amount
    
    def test_mint_by_non_owner_fails(self, w3, deployed_contract, accounts):
        """Test minting by non-owner fails"""
        mint_amount = Web3.to_wei(100, 'ether')
        
        # This should revert at the transaction level
        try:
            tx_hash = deployed_contract.functions.mint(accounts['user2'], mint_amount).transact({
                'from': accounts['user1'],  # Not the owner
                'gas': 200000
            })
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # If we get here, check that transaction failed
            assert tx_receipt.status == 0, "Transaction should have failed"
            
        except Exception as e:
            # Expected - transaction should revert
            assert "revert" in str(e).lower() or "execution reverted" in str(e).lower()
    
    def test_mint_to_zero_address_fails(self, w3, deployed_contract, accounts):
        """Test minting to zero address fails"""
        mint_amount = Web3.to_wei(100, 'ether')
        zero_address = "0x0000000000000000000000000000000000000000"
        
        try:
            tx_hash = deployed_contract.functions.mint(zero_address, mint_amount).transact({
                'from': accounts['owner'],
                'gas': 200000
            })
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            assert tx_receipt.status == 0, "Transaction should have failed"
        except Exception as e:
            # Expected - transaction should revert
            assert "revert" in str(e).lower() or "execution reverted" in str(e).lower()
    
    def test_mint_zero_amount_fails(self, w3, deployed_contract, accounts):
        """Test minting zero amount fails"""
        try:
            tx_hash = deployed_contract.functions.mint(accounts['user1'], 0).transact({
                'from': accounts['owner'],
                'gas': 200000
            })
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            assert tx_receipt.status == 0, "Transaction should have failed"
        except Exception as e:
            # Expected - transaction should revert
            assert "revert" in str(e).lower() or "execution reverted" in str(e).lower()

class TestOutflowCap:
    """Test AI/ML outflow cap functionality"""
    
    def test_set_outflow_cap_by_owner(self, w3, deployed_contract, accounts):
        """Test setting outflow cap by owner"""
        new_cap = Web3.to_wei(500, 'ether')  # 500 tokens
        
        # Set new cap
        tx_hash = deployed_contract.functions.setOutflowCap(new_cap).transact({
            'from': accounts['owner'],
            'gas': 100000
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        assert tx_receipt.status == 1, f"Transaction failed: {tx_receipt}"
        
        # Verify cap was set
        current_cap = deployed_contract.functions.outflowCap().call()
        assert current_cap == new_cap
    
    def test_set_outflow_cap_by_non_owner_fails(self, w3, deployed_contract, accounts):
        """Test setting outflow cap by non-owner fails"""
        new_cap = Web3.to_wei(200, 'ether')
        
        try:
            tx_hash = deployed_contract.functions.setOutflowCap(new_cap).transact({
                'from': accounts['user1'],  # Not owner
                'gas': 100000
            })
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            assert tx_receipt.status == 0, "Transaction should have failed"
        except Exception as e:
            # Expected - transaction should revert
            assert "revert" in str(e).lower() or "execution reverted" in str(e).lower()
    
    def test_set_zero_outflow_cap_fails(self, w3, deployed_contract, accounts):
        """Test setting zero outflow cap fails"""
        try:
            tx_hash = deployed_contract.functions.setOutflowCap(0).transact({
                'from': accounts['owner'],
                'gas': 100000
            })
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            assert tx_receipt.status == 0, "Transaction should have failed"
        except Exception as e:
            # Expected - transaction should revert
            assert "revert" in str(e).lower() or "execution reverted" in str(e).lower()

class TestBurning:
    """Test token burning with outflow cap"""
    
    def test_burn_within_cap_success(self, w3, deployed_contract, accounts):
        """Test burning within outflow cap succeeds"""
        # First ensure user has tokens to burn
        mint_amount = Web3.to_wei(200, 'ether')
        tx_hash = deployed_contract.functions.mint(accounts['user1'], mint_amount).transact({
            'from': accounts['owner']
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        assert tx_receipt.status == 1, "Mint transaction failed"
        
        # Set a reasonable outflow cap
        cap_amount = Web3.to_wei(500, 'ether')
        tx_hash = deployed_contract.functions.setOutflowCap(cap_amount).transact({
            'from': accounts['owner']
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        assert tx_receipt.status == 1, "Set cap transaction failed"
        
        # Burn tokens within cap
        burn_amount = Web3.to_wei(100, 'ether')  # Within 500 cap
        initial_balance = deployed_contract.functions.balanceOf(accounts['user1']).call()
        initial_supply = deployed_contract.functions.totalSupply().call()
        
        tx_hash = deployed_contract.functions.burn(burn_amount).transact({
            'from': accounts['user1'],
            'gas': 200000
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        assert tx_receipt.status == 1, "Burn transaction failed"
        
        # Verify burn succeeded
        final_balance = deployed_contract.functions.balanceOf(accounts['user1']).call()
        final_supply = deployed_contract.functions.totalSupply().call()
        
        assert initial_balance - final_balance == burn_amount
        assert initial_supply - final_supply == burn_amount
    
    def test_burn_beyond_cap_fails(self, w3, deployed_contract, accounts):
        """Test burning beyond outflow cap fails"""
        # First mint tokens to the account
        mint_amount = Web3.to_wei(200, 'ether')
        tx_hash = deployed_contract.functions.mint(accounts['user1'], mint_amount).transact({
            'from': accounts['owner']
        })
        w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Set a small outflow cap
        small_cap = Web3.to_wei(50, 'ether')  # 50 tokens
        tx_hash = deployed_contract.functions.setOutflowCap(small_cap).transact({
            'from': accounts['owner']
        })
        w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Try to burn more than cap
        large_burn = Web3.to_wei(100, 'ether')  # 100 tokens > 50 cap
        
        try:
            tx_hash = deployed_contract.functions.burn(large_burn).transact({
                'from': accounts['user1'],
                'gas': 200000
            })
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            assert tx_receipt.status == 0, "Transaction should have failed"
        except Exception as e:
            # Expected - transaction should revert
            assert "revert" in str(e).lower() or "execution reverted" in str(e).lower()
    
    def test_burn_insufficient_balance_fails(self, w3, deployed_contract, accounts):
        """Test burning more than balance fails"""
        # Check current balance
        current_balance = deployed_contract.functions.balanceOf(accounts['user2']).call()
        
        # Try to burn more than balance (or 1 ETH if balance is 0)
        excessive_burn = max(current_balance + Web3.to_wei(1, 'ether'), Web3.to_wei(1, 'ether'))
        
        try:
            tx_hash = deployed_contract.functions.burn(excessive_burn).transact({
                'from': accounts['user2'],
                'gas': 200000
            })
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            assert tx_receipt.status == 0, "Transaction should have failed"
        except Exception as e:
            # Expected - transaction should revert
            assert "revert" in str(e).lower() or "execution reverted" in str(e).lower()

class TestGreenFund:
    """Test sustainability green fund functionality"""
    
    def test_transfer_with_green_fund_fee(self, w3, deployed_contract, accounts):
        """Test transfers contribute to green fund"""
        # Ensure sender has tokens
        mint_amount = Web3.to_wei(1000, 'ether')
        tx_hash = deployed_contract.functions.mint(accounts['user1'], mint_amount).transact({
            'from': accounts['owner']
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        assert tx_receipt.status == 1, "Mint transaction failed"
        
        # Record initial balances
        transfer_amount = Web3.to_wei(100, 'ether')  # 100 tokens
        sender_initial = deployed_contract.functions.balanceOf(accounts['user1']).call()
        receiver_initial = deployed_contract.functions.balanceOf(accounts['user2']).call()
        green_fund_initial = deployed_contract.functions.balanceOf(accounts['green_fund']).call()
        
        # Make transfer
        tx_hash = deployed_contract.functions.transfer(accounts['user2'], transfer_amount).transact({
            'from': accounts['user1'],
            'gas': 200000
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        assert tx_receipt.status == 1, "Transfer transaction failed"
        
        # Check final balances
        sender_final = deployed_contract.functions.balanceOf(accounts['user1']).call()
        receiver_final = deployed_contract.functions.balanceOf(accounts['user2']).call()
        green_fund_final = deployed_contract.functions.balanceOf(accounts['green_fund']).call()
        
        # Calculate expected values (1% to green fund)
        green_fund_fee = transfer_amount // 100  # 1%
        actual_transfer = transfer_amount - green_fund_fee
        
        # Verify transfers
        assert sender_initial - sender_final == transfer_amount
        assert receiver_final - receiver_initial == actual_transfer
        assert green_fund_final - green_fund_initial == green_fund_fee
    
    def test_transfer_to_zero_address_fails(self, w3, deployed_contract, accounts):
        """Test transfer to zero address fails"""
        zero_address = "0x0000000000000000000000000000000000000000"
        transfer_amount = Web3.to_wei(10, 'ether')
        
        try:
            tx_hash = deployed_contract.functions.transfer(zero_address, transfer_amount).transact({
                'from': accounts['user1'],
                'gas': 200000
            })
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            assert tx_receipt.status == 0, "Transaction should have failed"
        except Exception as e:
            # Expected - transaction should revert
            assert "revert" in str(e).lower() or "execution reverted" in str(e).lower()

class TestAccessControl:
    """Test access control and security features"""
    
    def test_owner_functions_restricted(self, w3, deployed_contract, accounts):
        """Test owner-only functions are properly restricted"""
        owner = deployed_contract.functions.owner().call()
        assert owner.lower() == accounts['owner'].lower()
        
        # Test mint function restriction
        try:
            tx_hash = deployed_contract.functions.mint(accounts['user1'], Web3.to_wei(1, 'ether')).transact({
                'from': accounts['user1'],  # Not owner
                'gas': 200000
            })
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            # If transaction went through, it should have failed
            assert tx_receipt.status == 0, "Mint by non-owner should have failed"
        except Exception as e:
            # This is expected - transaction should revert
            assert "revert" in str(e).lower() or "execution reverted" in str(e).lower()
            
        # Test setOutflowCap function restriction
        try:
            tx_hash = deployed_contract.functions.setOutflowCap(Web3.to_wei(100, 'ether')).transact({
                'from': accounts['user1'],  # Not owner
                'gas': 200000
            })
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            # If transaction went through, it should have failed
            assert tx_receipt.status == 0, "SetOutflowCap by non-owner should have failed"
        except Exception as e:
            # This is expected - transaction should revert
            assert "revert" in str(e).lower() or "execution reverted" in str(e).lower()

class TestEmergencyFeatures:
    """Test emergency pause and reserve management"""
    
    def test_emergency_pause_toggle(self, w3, deployed_contract, accounts):
        """Test emergency pause functionality"""
        # Initially should not be paused
        assert deployed_contract.functions.emergencyPause().call() == False
        
        # Toggle pause
        tx_hash = deployed_contract.functions.togglePause().transact({
            'from': accounts['owner'],
            'gas': 100000
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        assert tx_receipt.status == 1, "Toggle pause transaction failed"
        
        # Should now be paused
        assert deployed_contract.functions.emergencyPause().call() == True
        
        # Toggle back
        tx_hash = deployed_contract.functions.togglePause().transact({
            'from': accounts['owner'],
            'gas': 100000
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        assert tx_receipt.status == 1, "Toggle pause transaction failed"
        
        # Should be unpaused
        assert deployed_contract.functions.emergencyPause().call() == False
    
    def test_reserves_update(self, w3, deployed_contract, accounts):
        """Test reserve amount updating"""
        new_reserve_amount = Web3.to_wei(50000, 'ether')  # 50k tokens equivalent
        
        # Update reserves
        tx_hash = deployed_contract.functions.updateReserves(new_reserve_amount).transact({
            'from': accounts['owner'],
            'gas': 100000
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        assert tx_receipt.status == 1, "Update reserves transaction failed"
        
        # Verify reserve amount
        current_reserves = deployed_contract.functions.totalReserves().call()
        assert current_reserves == new_reserve_amount

@pytest.mark.integration 
class TestIntegrationScenarios:
    """Integration tests simulating real-world usage"""
    
    def test_complete_lifecycle(self, w3, deployed_contract, accounts):
        """Test complete token lifecycle"""
        # Record initial state before our test
        initial_supply = deployed_contract.functions.totalSupply().call()
        initial_user1_balance = deployed_contract.functions.balanceOf(accounts['user1']).call()
        initial_user2_balance = deployed_contract.functions.balanceOf(accounts['user2']).call()
        initial_green_fund_balance = deployed_contract.functions.balanceOf(accounts['green_fund']).call()
        
        print(f"Initial state:")
        print(f"  Total supply: {Web3.from_wei(initial_supply, 'ether')} INDI")
        print(f"  User1 balance: {Web3.from_wei(initial_user1_balance, 'ether')} INDI")
        print(f"  User2 balance: {Web3.from_wei(initial_user2_balance, 'ether')} INDI")
        print(f"  Green fund balance: {Web3.from_wei(initial_green_fund_balance, 'ether')} INDI")
        
        # 1. Mint tokens for this test
        mint_amount = Web3.to_wei(10000, 'ether')
        tx_hash = deployed_contract.functions.mint(accounts['user1'], mint_amount).transact({
            'from': accounts['owner']
        })
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        assert tx_receipt.status == 1, "Mint transaction failed"
        
        # Verify mint worked
        after_mint_supply = deployed_contract.functions.totalSupply().call()
        after_mint_user1_balance = deployed_contract.functions.balanceOf(accounts['user1']).call()
        
        assert after_mint_supply == initial_supply + mint_amount
        assert after_mint_user1_balance == initial_user1_balance + mint_amount
        
        # 2. Multiple transfers (testing green fund accumulation)
        total_transfer_amount = Web3.to_wei(0, 'ether')  # Track total transfers
        
        for i in range(3):
            transfer_amount = Web3.to_wei(100, 'ether')
            total_transfer_amount += transfer_amount
            
            tx_hash = deployed_contract.functions.transfer(accounts['user2'], transfer_amount).transact({
                'from': accounts['user1']
            })
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            assert tx_receipt.status == 1, f"Transfer {i+1} transaction failed"
        
        # 3. Verify balances after transfers
        after_transfer_user1_balance = deployed_contract.functions.balanceOf(accounts['user1']).call()
        after_transfer_user2_balance = deployed_contract.functions.balanceOf(accounts['user2']).call()
        after_transfer_green_fund_balance = deployed_contract.functions.balanceOf(accounts['green_fund']).call()
        after_transfer_supply = deployed_contract.functions.totalSupply().call()
        
        print(f"\nAfter transfers:")
        print(f"  User1 balance: {Web3.from_wei(after_transfer_user1_balance, 'ether')} INDI")
        print(f"  User2 balance: {Web3.from_wei(after_transfer_user2_balance, 'ether')} INDI") 
        print(f"  Green fund balance: {Web3.from_wei(after_transfer_green_fund_balance, 'ether')} INDI")
        print(f"  Total supply: {Web3.from_wei(after_transfer_supply, 'ether')} INDI")
        
        # Calculate expected values
        total_green_fund_fee = total_transfer_amount // 100  # 1% fee
        expected_user1_balance = initial_user1_balance + mint_amount - total_transfer_amount
        expected_user2_received = total_transfer_amount - total_green_fund_fee
        expected_user2_balance = initial_user2_balance + expected_user2_received
        expected_green_fund_balance = initial_green_fund_balance + total_green_fund_fee
        
        print(f"\nExpected after transfers:")
        print(f"  User1 should have: {Web3.from_wei(expected_user1_balance, 'ether')} INDI")
        print(f"  User2 should have: {Web3.from_wei(expected_user2_balance, 'ether')} INDI")
        print(f"  Green fund should have: {Web3.from_wei(expected_green_fund_balance, 'ether')} INDI")
        
        # Verify transfers worked correctly
        assert after_transfer_user1_balance == expected_user1_balance
        assert after_transfer_user2_balance == expected_user2_balance
        assert after_transfer_green_fund_balance == expected_green_fund_balance
        
        # Supply should remain the same (no burning yet)
        assert after_transfer_supply == initial_supply + mint_amount
        
        # 4. Test burning with outflow cap
        burn_amount = Web3.to_wei(50, 'ether')
        
        # Ensure user2 has enough to burn
        user2_available = after_transfer_user2_balance
        if user2_available < burn_amount:
            burn_amount = user2_available  # Burn what's available
            print(f"Adjusted burn amount to {Web3.from_wei(burn_amount, 'ether')} INDI")
        
        if burn_amount > 0:
            # Set outflow cap high enough for the burn
            high_cap = burn_amount * 2  # Set cap higher than burn amount
            tx_hash = deployed_contract.functions.setOutflowCap(high_cap).transact({
                'from': accounts['owner']
            })
            w3.eth.wait_for_transaction_receipt(tx_hash)
            
            # Perform the burn
            tx_hash = deployed_contract.functions.burn(burn_amount).transact({
                'from': accounts['user2']
            })
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
            assert tx_receipt.status == 1, "Burn transaction failed"
            
            print(f"Burned: {Web3.from_wei(burn_amount, 'ether')} INDI")
            
            # 5. Verify final state
            final_supply = deployed_contract.functions.totalSupply().call()
            final_user2_balance = deployed_contract.functions.balanceOf(accounts['user2']).call()
            
            expected_final_supply = initial_supply + mint_amount - burn_amount
            expected_final_user2_balance = after_transfer_user2_balance - burn_amount
            
            print(f"\nFinal verification:")
            print(f"  Final supply: {Web3.from_wei(final_supply, 'ether')} INDI")
            print(f"  Expected final supply: {Web3.from_wei(expected_final_supply, 'ether')} INDI")
            print(f"  Final user2 balance: {Web3.from_wei(final_user2_balance, 'ether')} INDI")
            print(f"  Expected final user2 balance: {Web3.from_wei(expected_final_user2_balance, 'ether')} INDI")
            
            assert final_supply == expected_final_supply, f"Expected supply {Web3.from_wei(expected_final_supply, 'ether')}, got {Web3.from_wei(final_supply, 'ether')}"
            assert final_user2_balance == expected_final_user2_balance
        else:
            print("Skipping burn test - no tokens available to burn")
            # Just verify supply hasn't changed
            final_supply = deployed_contract.functions.totalSupply().call()
            assert final_supply == initial_supply + mint_amount