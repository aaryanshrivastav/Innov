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
          btc_holdings: firstTime ? 0 : btcHoldings || 0,
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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black text-white p-6">
      {/* Header */}
      <h1 className="text-4xl font-extrabold text-center mb-8 bg-gradient-to-r from-green-400 to-blue-500 bg-clip-text text-transparent">
        IndiCoin App
      </h1>

      {/* Investor Details */}
      <div className="max-w-3xl mx-auto bg-gray-800/70 backdrop-blur-md rounded-2xl shadow-2xl p-8 mb-10 border border-gray-700">
        <h2 className="text-xl font-semibold mb-6 text-green-400">
          Investor Details
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Balance */}
          <div>
            <label className="block text-sm mb-2 text-gray-300">
              Current Balance (Indicoin)
            </label>
            <input
              type="number"
              value={balance}
              onChange={(e) => setBalance(e.target.value)}
              placeholder="e.g., 1000"
              className="w-full p-3 rounded-lg bg-gray-900 border border-gray-700 focus:ring-2 focus:ring-green-500 focus:outline-none"
            />
          </div>

          {/* First-time Investor */}
          <div>
            <label className="block text-sm mb-2 text-gray-300">
              First-time Investor?
            </label>
            <div className="flex gap-4">
              <button
                className={`px-5 py-2 rounded-lg transition ${
                  firstTime
                    ? "bg-green-600 hover:bg-green-500 shadow-lg"
                    : "bg-gray-700 hover:bg-gray-600"
                }`}
                onClick={() => {
                  setFirstTime(true);
                  setBtcHoldings("");
                }}
              >
                Yes
              </button>
              <button
                className={`px-5 py-2 rounded-lg transition ${
                  !firstTime
                    ? "bg-green-600 hover:bg-green-500 shadow-lg"
                    : "bg-gray-700 hover:bg-gray-600"
                }`}
                onClick={() => setFirstTime(false)}
              >
                No
              </button>
            </div>
          </div>

          {/* Existing BTC Holdings */}
          <div>
            <label className="block text-sm mb-2 text-gray-300">
              Existing BTC Holdings
            </label>
            <input
              type="number"
              value={btcHoldings}
              onChange={(e) => setBtcHoldings(e.target.value)}
              placeholder="e.g., 0.05"
              disabled={firstTime}
              className={`w-full p-3 rounded-lg border transition ${
                firstTime
                  ? "bg-gray-700 text-gray-500 cursor-not-allowed border-gray-600"
                  : "bg-gray-900 border-gray-700 focus:ring-2 focus:ring-green-500"
              }`}
            />
          </div>

          {/* Risk Profile */}
          <div>
            <label className="block text-sm mb-2 text-gray-300">
              Risk Profile
            </label>
            <select
              value={riskProfile}
              onChange={(e) => setRiskProfile(e.target.value)}
              className="w-full p-3 rounded-lg bg-gray-900 border border-gray-700 focus:ring-2 focus:ring-green-500 focus:outline-none"
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
          className="mt-8 w-full px-6 py-3 bg-green-600 rounded-lg shadow-lg hover:bg-green-500 transition font-semibold disabled:opacity-50"
        >
          {loading ? "Generating..." : "Generate"}
        </button>
      </div>

      {/* Results Section */}
      {result && (
        <div className="max-w-3xl mx-auto bg-gray-800/70 backdrop-blur-md rounded-2xl shadow-2xl p-8 border border-gray-700 animate-fadeIn">
          <h2 className="text-xl font-semibold mb-6 text-green-400">
            Prediction Results
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <ResultCard label="BTC/USD" value={`$${result.BTC_USD}`} />
            <ResultCard label="USD/INR" value={`₹${result.USD_INR}`}/>
            <ResultCard label="Indicoin Balance" value={balance} />
            <ResultCard label="Hard Limit (Indicoin)" value={result.Hard_Limit} />
          </div>
        </div>
      )}
    </div>
  );
}

/* Result Card Component */
function ResultCard({ label, value }) {
  return (
    <div className="p-6 bg-gray-900 rounded-xl shadow-md hover:shadow-lg transition transform hover:-translate-y-1">
      <p className="text-sm text-gray-400">{label}</p>
      <p className="text-2xl font-bold text-white mt-1">{value}</p>
    </div>
  );
}
