import React, { useState } from "react";
import axios from "axios";

export default function IndiCoinApp() {
  const [balance, setBalance] = useState("");
  const [firstTime, setFirstTime] = useState(true);
  const [btcHoldings, setBtcHoldings] = useState("");
  const [riskProfile, setRiskProfile] = useState("moderate");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!balance) return alert("Please enter your balance.");

    setLoading(true);
    try {
      const res = await axios.get("http://localhost:8000/predict", {
        params: {
          user_balance: balance,
          first_time: firstTime,
          btc_holdings: firstTime ? 0 : btcHoldings || 0, // force 0 if first-time
          risk_profile: riskProfile,
        },
      });
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Error generating prediction");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      <h1 className="text-2xl font-bold mb-4">IndiCoin dApp</h1>

      {/* Investor Details */}
      <div className="bg-gray-800 rounded-2xl shadow-lg p-6 mb-6">
        <h2 className="text-lg font-semibold mb-4">Investor Details</h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Balance */}
          <div>
            <label className="block text-sm mb-1">Current Balance (USD)</label>
            <input
              type="number"
              value={balance}
              onChange={(e) => setBalance(e.target.value)}
              placeholder="e.g., 1000"
              className="w-full p-2 rounded bg-gray-700 border border-gray-600"
            />
          </div>

          {/* First-time Investor */}
          <div>
            <label className="block text-sm mb-1">First-time Investor?</label>
            <div className="flex gap-4 mt-1">
              <button
                className={`px-4 py-2 rounded-lg ${
                  firstTime ? "bg-blue-600" : "bg-gray-700"
                }`}
                onClick={() => {
                  setFirstTime(true);
                  setBtcHoldings(""); // clear btc holdings if yes
                }}
              >
                Yes
              </button>
              <button
                className={`px-4 py-2 rounded-lg ${
                  !firstTime ? "bg-blue-600" : "bg-gray-700"
                }`}
                onClick={() => setFirstTime(false)}
              >
                No
              </button>
            </div>
          </div>

          {/* Existing BTC Holdings */}
          <div>
            <label className="block text-sm mb-1">Existing BTC Holdings</label>
            <input
              type="number"
              value={btcHoldings}
              onChange={(e) => setBtcHoldings(e.target.value)}
              placeholder="e.g., 0.05"
              disabled={firstTime}
              className={`w-full p-2 rounded border ${
                firstTime
                  ? "bg-gray-600 text-gray-400 cursor-not-allowed border-gray-500"
                  : "bg-gray-700 border-gray-600"
              }`}
            />
          </div>

          {/* Risk Profile */}
          <div>
            <label className="block text-sm mb-1">Risk Profile</label>
            <select
              value={riskProfile}
              onChange={(e) => setRiskProfile(e.target.value)}
              className="w-full p-2 rounded bg-gray-700 border border-gray-600"
            >
              <option value="conservative">Conservative</option>
              <option value="moderate">Moderate</option>
              <option value="aggressive">Aggressive</option>
            </select>
          </div>
        </div>

        {/* Generate Button */}
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="mt-6 px-6 py-2 bg-green-600 rounded-lg shadow hover:bg-green-500 disabled:opacity-50"
        >
          {loading ? "Generating..." : "Generate"}
        </button>
      </div>

      {/* Results Section */}
      {result && (
        <div className="bg-gray-800 rounded-2xl shadow-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Prediction Results</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-gray-700 rounded-lg shadow">
              <p className="text-sm text-gray-400">BTC/USD</p>
              <p className="text-xl font-bold">${result.BTC_USD}</p>
            </div>
            <div className="p-4 bg-gray-700 rounded-lg shadow">
              <p className="text-sm text-gray-400">USD/INR</p>
              <p className="text-xl font-bold">{result.USD_INR}</p>
            </div>
            <div className="p-4 bg-gray-700 rounded-lg shadow">
              <p className="text-sm text-gray-400">Indicoin Balance</p>
              <p className="text-xl font-bold">{balance}</p>
            </div>
            <div className="p-4 bg-gray-700 rounded-lg shadow">
              <p className="text-sm text-gray-400">Hard Limit (INR)</p>
              <p className="text-xl font-bold">{result.Hard_Limit}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
