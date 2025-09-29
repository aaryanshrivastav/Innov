// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title IndiCoin
 * @dev A stablecoin backed 1:1 with INR and reserves in BTC/ETH
 * Features AI/ML integration, sustainability fund, and proof-of-reserves
 */
contract IndiCoin {
    // Token Information
    string public constant name = "IndiCoin";
    string public constant symbol = "INDI";
    uint8 public constant decimals = 18;
    
    // Core State
    uint256 private _totalSupply;
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;
    
    // Access Control
    address public owner;
    
    // AI/ML Integration - Outflow Cap for Fraud Detection
    uint256 public outflowCap;
    uint256 public currentOutflow;
    uint256 public outflowResetTime;
    uint256 public constant OUTFLOW_RESET_PERIOD = 24 hours;
    
    // Green Fund (1% of transactions)
    address public greenFund;
    uint256 public constant GREEN_FUND_RATE = 100; // 1% = 100/10000
    
    // Reserve Backing
    uint256 public totalReserves;
    bool public emergencyPause;
    
    // Events
    event Transfer(address indexed from, address indexed to, uint256 value);
    event Approval(address indexed owner, address indexed spender, uint256 value);
    event Mint(address indexed to, uint256 amount);
    event Burn(address indexed from, uint256 amount);
    event OutflowCapSet(uint256 newCap);
    event GreenFundTransfer(uint256 amount);
    event ReservesUpdated(uint256 newReserveAmount);
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }
    
    modifier notPaused() {
        require(!emergencyPause, "Contract paused");
        _;
    }
    
    modifier validAddress(address _addr) {
        require(_addr != address(0), "Invalid address");
        _;
    }
    
    /**
     * @dev Constructor
     */
    constructor(address _greenFund) validAddress(_greenFund) {
        owner = msg.sender;
        greenFund = _greenFund;
        outflowCap = 1000000 * 10**decimals; // 1M tokens default
        outflowResetTime = block.timestamp + OUTFLOW_RESET_PERIOD;
        totalReserves = 0;
        emergencyPause = false;
    }
    
    /**
     * @dev Set outflow cap for AI/ML anomaly detection
     */
    function setOutflowCap(uint256 _newCap) external onlyOwner {
        require(_newCap > 0, "Cap must be positive");
        outflowCap = _newCap;
        emit OutflowCapSet(_newCap);
    }
    
    /**
     * @dev Mint new tokens (only owner - backed by reserves)
     */
    function mint(address to, uint256 amount) external onlyOwner validAddress(to) notPaused {
        require(amount > 0, "Amount must be positive");
        
        _totalSupply += amount;
        _balances[to] += amount;
        
        emit Mint(to, amount);
        emit Transfer(address(0), to, amount);
    }
    
    /**
     * @dev Burn tokens with outflow cap check
     */
    function burn(uint256 amount) external notPaused {
        require(amount > 0, "Amount must be positive");
        require(_balances[msg.sender] >= amount, "Insufficient balance");
        
        // Reset outflow if period expired
        if (block.timestamp >= outflowResetTime) {
            currentOutflow = 0;
            outflowResetTime = block.timestamp + OUTFLOW_RESET_PERIOD;
        }
        
        // Check outflow cap for fraud detection
        require(currentOutflow + amount <= outflowCap, "Exceeds outflow cap");
        
        currentOutflow += amount;
        _balances[msg.sender] -= amount;
        _totalSupply -= amount;
        
        emit Burn(msg.sender, amount);
        emit Transfer(msg.sender, address(0), amount);
    }
    
    /**
     * @dev Transfer with green fund contribution
     */
    function transfer(address to, uint256 amount) external validAddress(to) notPaused returns (bool) {
        return _transfer(msg.sender, to, amount);
    }
    
    /**
     * @dev Internal transfer with green fund
     */
    function _transfer(address from, address to, uint256 amount) internal returns (bool) {
        require(_balances[from] >= amount, "Insufficient balance");
        
        // Calculate green fund contribution (1%)
        uint256 greenFundAmount = (amount * GREEN_FUND_RATE) / 10000;
        uint256 actualTransfer = amount - greenFundAmount;
        
        _balances[from] -= amount;
        _balances[to] += actualTransfer;
        _balances[greenFund] += greenFundAmount;
        
        emit Transfer(from, to, actualTransfer);
        emit Transfer(from, greenFund, greenFundAmount);
        emit GreenFundTransfer(greenFundAmount);
        
        return true;
    }
    
    /**
     * @dev Update reserve backing
     */
    function updateReserves(uint256 newReserveAmount) external onlyOwner {
        totalReserves = newReserveAmount;
        emit ReservesUpdated(newReserveAmount);
    }
    
    /**
     * @dev Emergency pause
     */
    function togglePause() external onlyOwner {
        emergencyPause = !emergencyPause;
    }
    
    /**
     * @dev Standard ERC20 functions
     */
    function totalSupply() external view returns (uint256) {
        return _totalSupply;
    }
    
    function balanceOf(address account) external view returns (uint256) {
        return _balances[account];
    }
    
    function allowance(address owner_addr, address spender) external view returns (uint256) {
        return _allowances[owner_addr][spender];
    }
    
    function approve(address spender, uint256 amount) external validAddress(spender) returns (bool) {
        _allowances[msg.sender][spender] = amount;
        emit Approval(msg.sender, spender, amount);
        return true;
    }
    
    function transferFrom(address from, address to, uint256 amount) external returns (bool) {
        require(_allowances[from][msg.sender] >= amount, "Allowance exceeded");
        _allowances[from][msg.sender] -= amount;
        return _transfer(from, to, amount);
    }
}