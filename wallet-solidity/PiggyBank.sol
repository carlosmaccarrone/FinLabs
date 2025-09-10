// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract PiggyBank {
    address public owner;

    constructor() {
        owner = msg.sender; // who deploys is the owner
    }

    // Event to log deposits
    event Deposit(address indexed sender, uint amount);

    // Event to log in withdrawals
    event Withdraw(address indexed to, uint amount);

    // Receive ETH
    receive() external payable {
        emit Deposit(msg.sender, msg.value);
    }

    // Withdraw ETH (owner only)
    function withdraw() external {
        require(msg.sender == owner, "You are not the owner!");
        uint balance = address(this).balance;
        payable(owner).transfer(balance);
        emit Withdraw(owner, balance);
    }

    // View contract balance
    function getBalance() external view returns (uint) {
        return address(this).balance;
    }
}
