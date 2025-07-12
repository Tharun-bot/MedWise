import json
import os

# Paths (adjust if needed)
input_path = "artifacts/contracts/MedWise.sol/MedWise.json"
output_path = "../backend/contracts/abi/MedWise.json"  # relative to blockchain/

# Load full JSON artifact
with open(input_path, "r") as f:
    contract_data = json.load(f)

# Extract ABI
abi = contract_data.get("abi", [])

# Ensure output folder exists
os.makedirs(os.path.dirname(output_path), exist_ok=True)

# Write ABI to file
with open(output_path, "w") as f:
    json.dump(abi, f, indent=2)

print(f"✅ ABI extracted to {output_path}")
