#!/usr/bin/env python3
"""
Simple test to check if everything is working
"""

import pytest
from web3 import Web3
import json
from pathlib import Path

def test_web3_connection():
    """Test if we can connect to Ganache"""
    print("Testing Web3 connection...")
    w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
    
    print(f"Connected: {w3.is_connected()}")
    if w3.is_connected():
        print(f"Accounts available: {len(w3.eth.accounts)}")
        print(f"First account: {w3.eth.accounts[0]}")
    
    assert w3.is_connected(), "Cannot connect to Ganache"

def test_contract_files_exist():
    """Test if contract files exist"""
    print("Checking contract files...")
    
    build_dir = Path("build")
    print(f"Build directory exists: {build_dir.exists()}")
    
    abi_file = build_dir / "IndiCoin_abi.json"
    print(f"ABI file exists: {abi_file.exists()}")
    
    bytecode_file = build_dir / "IndiCoin_bytecode.txt"
    print(f"Bytecode file exists: {bytecode_file.exists()}")
    
    if abi_file.exists():
        with open(abi_file, 'r') as f:
            abi = json.load(f)
        print(f"ABI has {len(abi)} functions")
    
    assert build_dir.exists(), "Build directory not found"
    assert abi_file.exists(), "ABI file not found"
    assert bytecode_file.exists(), "Bytecode file not found"

if __name__ == "__main__":
    test_web3_connection()
    test_contract_files_exist()
    print("All basic checks passed!")