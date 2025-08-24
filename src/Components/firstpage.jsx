import React, { useState } from "react";

export default function FirstPage() {
  const [activeTab, setActiveTab] = useState('overview');

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Navigation */}
      <nav className="bg-gray-800 border-b border-gray-700 px-6 py-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-white">IndiCoin</h1>
          <div className="flex space-x-6">
            <a href="#" className="text-gray-300 hover:text-white transition">Platform</a>
            <a href="#" className="text-gray-300 hover:text-white transition">Documentation</a>
            <a href="#" className="text-gray-300 hover:text-white transition">Support</a>
            <button className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-lg transition">
              Login
            </button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="px-6 py-16 text-center">
        <div className="max-w-4xl mx-auto">
          <h1 className="text-6xl font-bold text-white tracking-tight mb-6">IndiCoin</h1>
          <p className="text-xl text-gray-300 max-w-2xl mx-auto leading-relaxed mb-8">
            India's premier digital currency infrastructure built on sustainable blockchain technology.
            INR-backed stability with institutional-grade security and compliance.
          </p>
          
          {/* Key Metrics */}
          <div className="grid md:grid-cols-3 gap-6 mb-12">
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
              <div className="text-3xl font-bold text-green-400">₹100Cr+</div>
              <div className="text-gray-400">Reserve Backing</div>
            </div>
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
              <div className="text-3xl font-bold text-blue-400">99.9%</div>
              <div className="text-gray-400">Platform Uptime</div>
            </div>
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-6">
              <div className="text-3xl font-bold text-purple-400">ISO 27001</div>
              <div className="text-gray-400">Security Certified</div>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row justify-center gap-4">
            <button className="px-8 py-4 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-all duration-200 font-semibold">
              Access Platform
            </button>
            <button className="px-8 py-4 bg-gray-700 hover:bg-gray-600 text-white border border-gray-600 rounded-xl transition-all duration-200 font-semibold">
              View Reserves
            </button>
          </div>
        </div>
      </section>

      {/* Dashboard Section */}
      <section className="px-6 py-16 bg-gray-800">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Platform Dashboard</h2>
          
          {/* Dashboard Navigation */}
          <div className="flex justify-center mb-8">
            <div className="bg-gray-700 p-1 rounded-lg">
              {['overview', 'trading', 'portfolio', 'analytics'].map((tab) => (
                <button
                  key={tab}
                  onClick={() => setActiveTab(tab)}
                  className={`px-6 py-2 rounded-md capitalize transition ${
                    activeTab === tab 
                      ? 'bg-blue-600 text-white' 
                      : 'text-gray-300 hover:text-white'
                  }`}
                >
                  {tab}
                </button>
              ))}
            </div>
          </div>

          {/* Dashboard Content */}
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Main Dashboard Panel */}
            <div className="lg:col-span-2 bg-gray-900 border border-gray-700 rounded-xl p-6">
              {activeTab === 'overview' && (
                <>
                  <h3 className="text-xl font-bold mb-6">Portfolio Overview</h3>
                  <div className="grid md:grid-cols-2 gap-4 mb-6">
                    <div className="bg-gray-800 p-4 rounded-lg">
                      <div className="text-sm text-gray-400">Total Balance</div>
                      <div className="text-2xl font-bold text-green-400">₹2,45,680</div>
                      <div className="text-sm text-green-400">+12.5% (24h)</div>
                    </div>
                    <div className="bg-gray-800 p-4 rounded-lg">
                      <div className="text-sm text-gray-400">Available Balance</div>
                      <div className="text-2xl font-bold">₹1,85,420</div>
                      <div className="text-sm text-gray-400">Ready to trade</div>
                    </div>
                  </div>
                  
                  {/* Chart Placeholder */}
                  <div className="bg-gray-800 p-6 rounded-lg h-64 flex items-center justify-center">
                    <div className="text-center">
                      <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                        <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                          <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z" />
                        </svg>
                      </div>
                      <div className="text-gray-400">Portfolio Performance Chart</div>
                    </div>
                  </div>
                </>
              )}

              {activeTab === 'trading' && (
                <>
                  <h3 className="text-xl font-bold mb-6">Trading Interface</h3>
                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-gray-800 p-4 rounded-lg">
                      <h4 className="font-semibold mb-4 text-green-400">Buy IndiCoin</h4>
                      <div className="space-y-4">
                        <input
                          type="number"
                          placeholder="Amount (INR)"
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                        />
                        <div className="text-sm text-gray-400">
                          Rate: 1 INDI = ₹1.00
                        </div>
                        <button className="w-full bg-green-600 hover:bg-green-700 py-2 rounded-lg transition">
                          Buy INDI
                        </button>
                      </div>
                    </div>
                    
                    <div className="bg-gray-800 p-4 rounded-lg">
                      <h4 className="font-semibold mb-4 text-red-400">Sell IndiCoin</h4>
                      <div className="space-y-4">
                        <input
                          type="number"
                          placeholder="Amount (INDI)"
                          className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-2 text-white"
                        />
                        <div className="text-sm text-gray-400">
                          Rate: 1 INDI = ₹0.998
                        </div>
                        <button className="w-full bg-red-600 hover:bg-red-700 py-2 rounded-lg transition">
                          Sell INDI
                        </button>
                      </div>
                    </div>
                  </div>
                </>
              )}

              {activeTab === 'portfolio' && (
                <>
                  <h3 className="text-xl font-bold mb-6">Asset Portfolio</h3>
                  <div className="space-y-4">
                    <div className="bg-gray-800 p-4 rounded-lg flex justify-between items-center">
                      <div>
                        <div className="font-semibold">IndiCoin (INDI)</div>
                        <div className="text-sm text-gray-400">2,45,680 INDI</div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-green-400">₹2,45,680</div>
                        <div className="text-sm text-green-400">+12.5%</div>
                      </div>
                    </div>
                    
                    <div className="bg-gray-800 p-4 rounded-lg flex justify-between items-center">
                      <div>
                        <div className="font-semibold">Staked INDI</div>
                        <div className="text-sm text-gray-400">50,000 INDI</div>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold">₹50,000</div>
                        <div className="text-sm text-blue-400">5.2% APY</div>
                      </div>
                    </div>
                  </div>
                </>
              )}

              {activeTab === 'analytics' && (
                <>
                  <h3 className="text-xl font-bold mb-6">Performance Analytics</h3>
                  <div className="grid md:grid-cols-2 gap-4 mb-6">
                    <div className="bg-gray-800 p-4 rounded-lg">
                      <div className="text-sm text-gray-400">30-Day Return</div>
                      <div className="text-2xl font-bold text-green-400">+18.7%</div>
                    </div>
                    <div className="bg-gray-800 p-4 rounded-lg">
                      <div className="text-sm text-gray-400">Total Transactions</div>
                      <div className="text-2xl font-bold">147</div>
                    </div>
                  </div>
                  
                  <div className="bg-gray-800 p-6 rounded-lg">
                    <h4 className="font-semibold mb-4">Recent Transactions</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between items-center py-2 border-b border-gray-700">
                        <div>
                          <div className="text-sm font-medium">Buy INDI</div>
                          <div className="text-xs text-gray-400">2 hours ago</div>
                        </div>
                        <div className="text-green-400">+10,000 INDI</div>
                      </div>
                      <div className="flex justify-between items-center py-2 border-b border-gray-700">
                        <div>
                          <div className="text-sm font-medium">Stake Rewards</div>
                          <div className="text-xs text-gray-400">1 day ago</div>
                        </div>
                        <div className="text-green-400">+260 INDI</div>
                      </div>
                      <div className="flex justify-between items-center py-2">
                        <div>
                          <div className="text-sm font-medium">Buy INDI</div>
                          <div className="text-xs text-gray-400">3 days ago</div>
                        </div>
                        <div className="text-green-400">+25,000 INDI</div>
                      </div>
                    </div>
                  </div>
                </>
              )}
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Market Info */}
              <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
                <h3 className="text-lg font-bold mb-4">Market Information</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Current Price</span>
                    <span className="text-green-400">₹1.00</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">24h Volume</span>
                    <span>₹12.5Cr</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Market Cap</span>
                    <span>₹890Cr</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Circulating Supply</span>
                    <span>890M INDI</span>
                  </div>
                </div>
              </div>

              {/* Reserve Status */}
              <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
                <h3 className="text-lg font-bold mb-4">Reserve Status</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Reserves</span>
                    <span className="text-green-400">₹890Cr</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Collateral Ratio</span>
                    <span className="text-green-400">100%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Last Audit</span>
                    <span>Jan 15, 2025</span>
                  </div>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2 mt-4">
                  <div className="bg-green-400 h-2 rounded-full" style={{width: '100%'}}></div>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="bg-gray-900 border border-gray-700 rounded-xl p-6">
                <h3 className="text-lg font-bold mb-4">Quick Actions</h3>
                <div className="space-y-3">
                  <button className="w-full bg-blue-600 hover:bg-blue-700 py-2 rounded-lg transition">
                    Deposit INR
                  </button>
                  <button className="w-full bg-gray-700 hover:bg-gray-600 py-2 rounded-lg transition">
                    Withdraw INR
                  </button>
                  <button className="w-full bg-purple-600 hover:bg-purple-700 py-2 rounded-lg transition">
                    Stake INDI
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="px-6 py-16">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Why Choose IndiCoin</h2>
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
              <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3">Enterprise Security</h3>
              <p className="text-gray-400 leading-relaxed">
                Bank-grade security infrastructure with multi-signature wallets, cold storage protocols, 
                and real-time fraud detection systems ensuring institutional-level asset protection.
              </p>
            </div>

            <div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
              <div className="w-12 h-12 bg-green-600 rounded-xl flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3">AI-Powered Compliance</h3>
              <p className="text-gray-400 leading-relaxed">
                Advanced machine learning algorithms provide real-time AML/KYC monitoring, 
                regulatory compliance automation, and risk assessment for seamless operations.
              </p>
            </div>

            <div className="bg-gray-800 border border-gray-700 rounded-xl p-8">
              <div className="w-12 h-12 bg-purple-600 rounded-xl flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold mb-3">Sustainable Impact</h3>
              <p className="text-gray-400 leading-relaxed">
                Carbon-neutral operations with dedicated ESG investment programs supporting 
                UN Sustainable Development Goals and environmental conservation initiatives.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 px-6 py-8">
        <div className="max-w-6xl mx-auto text-center">
          <div className="text-gray-400 text-sm space-y-2">
            <div className="flex justify-center space-x-6 mt-4">
              <a href="#" className="text-gray-500 hover:text-gray-300">Privacy Policy</a>
              <a href="#" className="text-gray-500 hover:text-gray-300">Terms of Service</a>
              <a href="#" className="text-gray-500 hover:text-gray-300">Contact</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}