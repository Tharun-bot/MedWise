// scripts/deploy_medwise.js
const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
    const [deployer] = await hre.ethers.getSigners();
    console.log("Deploying contract with account:", deployer.address);

    const MedWise = await hre.ethers.getContractFactory("MedWise");
    const contract = await MedWise.deploy(); // Deploy here
    await contract.waitForDeployment();      // ✅ Use this with Ethers v6+

    const contractAddress = await contract.getAddress(); // ✅ Ethers v6+

    console.log("Contract deployed to:", contractAddress);

    // In deploy_medwise.js
    const backendPath = path.join(__dirname, "../../../backend/contract_address.json");
    fs.writeFileSync(
    backendPath,
    JSON.stringify({ address: contractAddress }, null, 2)
    );

}

main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
});
