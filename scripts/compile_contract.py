#!/usr/bin/env python3
"""
Simplified IndiCoin Compilation Script
Handles dependency issues more gracefully
"""

import json
import os
from pathlib import Path

def install_solc():
    """Install Solidity compiler"""
    try:
        from solcx import install_solc, set_solc_version
        print("🔧 Installing Solidity compiler...")
        install_solc("0.8.19")
        set_solc_version("0.8.19")
        print("✅ Solidity 0.8.19 ready")
        return True
    except Exception as e:
        print(f"❌ Solc installation failed: {e}")
        return False

def read_contract():
    """Read the contract source"""
    contract_path = Path("contracts/IndiCoin.sol")
    
    if not contract_path.exists():
        print(f"❌ Contract not found at {contract_path}")
        print("💡 Make sure contracts/IndiCoin.sol exists")
        return None
    
    try:
        with open(contract_path, "r", encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"❌ Failed to read contract: {e}")
        return None

def compile_contract():
    """Compile the IndiCoin contract"""
    print("🚀 IndiCoin Simple Compilation")
    print("=" * 40)
    
    # Install Solc
    if not install_solc():
        return False
    
    # Read contract
    contract_source = read_contract()
    if not contract_source:
        return False
    
    print("📝 Contract source loaded")
    
    try:
        from solcx import compile_standard
        
        # Simple compilation input
        solc_input = {
            "language": "Solidity",
            "sources": {
                "IndiCoin.sol": {
                    "content": contract_source
                }
            },
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "evm.bytecode", "evm.deployedBytecode"]
                    }
                },
                "optimizer": {
                    "enabled": True,
                    "runs": 200
                }
            }
        }
        
        print("🔨 Compiling contract...")
        compiled_sol = compile_standard(solc_input, solc_version="0.8.19")
        
        print("✅ Contract compiled successfully!")
        
        # Create build directory
        build_dir = Path("build")
        build_dir.mkdir(exist_ok=True)
        
        # Extract contract data
        contract_data = compiled_sol["contracts"]["IndiCoin.sol"]["IndiCoin"]
        
        # Save ABI
        abi = contract_data["abi"]
        with open(build_dir / "IndiCoin_abi.json", "w") as f:
            json.dump(abi, f, indent=2)
        
        # Save bytecode
        bytecode = contract_data["evm"]["bytecode"]["object"]
        with open(build_dir / "IndiCoin_bytecode.txt", "w") as f:
            f.write(bytecode)
        
        # Save full compilation
        with open(build_dir / "IndiCoin_full.json", "w") as f:
            json.dump(compiled_sol, f, indent=2)
        
        print("💾 Artifacts saved:")
        print(f"   - ABI: build/IndiCoin_abi.json")
        print(f"   - Bytecode: build/IndiCoin_bytecode.txt")
        print(f"   - Full: build/IndiCoin_full.json")
        
        # Validate
        if len(abi) < 10:
            print("❌ ABI seems too small")
            return False
        
        if len(bytecode) < 1000:
            print("❌ Bytecode seems too small")
            return False
        
        # Check for required functions
        function_names = [item["name"] for item in abi if item["type"] == "function"]
        required_functions = ["mint", "burn", "setOutflowCap", "transfer", "balanceOf", "totalSupply"]
        
        missing = set(required_functions) - set(function_names)
        if missing:
            print(f"❌ Missing functions: {missing}")
            return False
        
        print(f"✅ Contract has {len(function_names)} functions")
        print("🎉 Compilation successful!")
        
        return True
        
    except Exception as e:
        print(f"❌ Compilation failed: {e}")
        return False

if __name__ == "__main__":
    success = compile_contract()
    
    if success:
        print("\n🎉 SUCCESS!")
        print("📦 Ready for testing and deployment!")
        print("\nNext steps:")
        print("1. python test_simple.py")
        print("2. python scripts/test_contract.py")
    else:
        print("\n❌ FAILED!")
        print("Check the errors above and try again")
    
    exit(0 if success else 1)