# PiggyBank Contract 🐷💰

A simple Solidity smart contract that works like a piggy bank.  
Anyone can deposit ETH into the contract, but only the owner (the deployer) can withdraw the funds.

## Features

- **Owner-only withdrawals**: only the account that deployed the contract can withdraw all funds.
- **Deposits**: anyone can send ETH directly to the contract.
- **Events**: logs deposits and withdrawals for easy tracking.
- **Balance check**: view the current ETH balance stored in the contract.

## How to Use

1. Deploy the contract
- Use Remix IDE.
- Select Solidity compiler ```^0.8.0```.
- Deploy the contract on a testnet (e.g. Sepolia or Holesky) using MetaTask.

2. Deposit ETH
- Send ETH directly to the contract address, or use the **"Transact"** button in Remix.

3. Withdraw ETH
- Call the ```withdraw()``` function.
- Only the owner (deployer address) can withdraw.

4. Check balance
- Call ```getBalance()``` to see how much ETH is stored.

## Example Workflow

1. Deploy contract with your wallet → you become the owner.
2. Anyone (including you) can deposit ETH.
3. Balance grows with each deposit.
4. Owner calls ```withdraw()``` → all ETH goes back to the owner wallet.

You can deploy the script in an online Remix ide https://remix.ethereum.org 

---

⚡️ This contract is for learning purposes. Do not use it in production with real funds.