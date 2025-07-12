from web3 import Web3
import json
import os

WEB3_PROVIDER_URI = "http://127.0.0.1:8545"
PRIVATE_KEY = "0xde9be858da4a475276426320d5e9262ecfc3ba460bfac56360bfa6c4c28b4ee0"
WALLET_ADDRESS = "0xdD2FD4581271e230360230F9337D5c0430Bf44C0"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

ADDRESS_JSON_PATH = os.path.join(os.path.dirname(__file__), "../contract_address.json")
with open(ADDRESS_JSON_PATH, "r") as f:
    CONTRACT_ADDRESS = json.load(f)["address"]

# ✅ Step 2: Load ABI
ABI_PATH = os.path.join(os.path.dirname(__file__), "abi", "MedWise.json")
with open(ABI_PATH, "r") as f:
    abi = json.load(f)
    final_abi = abi if isinstance(abi, list) else abi.get("abi")

if not final_abi:
    raise ValueError("ABI structure invalid or empty")

# ✅ Step 3: Setup web3 instance
web3 = Web3(Web3.HTTPProvider(WEB3_PROVIDER_URI))
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=final_abi)
w3 = web3  # Exportable alias
