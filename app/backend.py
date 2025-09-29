import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from mint_tokens import mint
from burn_tokens import burn 
from lstm import get_prediction  

load_dotenv()
app = Flask(__name__)

INDICOIN_RATE = 100  # 1 Indicoin = 100 INR

@app.route("/mint", methods=["POST"])
def mint_tokens():
    try:
        data = request.get_json()

        if not data or "inr_amount" not in data:
            return jsonify({"error": "Missing 'inr_amount' in request body"}), 400

        inr_amount = float(data["inr_amount"])
        if inr_amount <= 0:
            return jsonify({"error": "INR amount must be greater than zero"}), 400

        indicoin_amount = int(inr_amount / INDICOIN_RATE)
        if indicoin_amount == 0:
            return jsonify({"error": "INR amount too low to mint any Indicoin"}), 400

        recipient_address = os.getenv("ACCOUNT_ADDRESS")
        if not recipient_address:
            return jsonify({"error": "Missing ACCOUNT_ADDRESS in environment"}), 500

        # Mint tokens
        mint(recipient_address, indicoin_amount)

        return jsonify({
            "message": f"Successfully minted {indicoin_amount} IndiCoin",
            "recipient": recipient_address,
            "inr_provided": inr_amount,
            "indicoin_minted": indicoin_amount
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/setoutputflow", methods=["POST"])
def set_output_flow():
    try:
        data = request.get_json()

        if not data or "inr_amount" not in data:
            return jsonify({"error": "Missing 'inr_amount' in request body"}), 400

        inr_amount = float(data["inr_amount"])
        if inr_amount <= 0:
            return jsonify({"error": "INR amount must be greater than zero"}), 400

        first_time = bool(data.get("first_time", False))
        btc_holdings = float(data.get("btc_holdings", 0.0))
        risk_profile = data.get("risk_profile", "moderate")

        indicoin_amount = inr_amount / INDICOIN_RATE
        if indicoin_amount <= 0:
            return jsonify({"error": "INR amount too low to mint any Indicoin"}), 400

        result = get_prediction(
            indicoin_balance=indicoin_amount,
            first_time=first_time,
            btc_holdings=btc_holdings,
            risk_profile=risk_profile
        )

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/burn", methods=["POST"])
def burn_tokens():
    try:
        data = request.get_json()
        if not data or "amount" not in data:
            return jsonify({"error": "Missing 'amount' in request body"}), 400

        amount = int(data["amount"])
        if amount <= 0:
            return jsonify({"error": "Amount must be greater than zero"}), 400

        burn(amount)

        return jsonify({
            "message": f"Successfully burned {amount} IndiCoin",
            "amount_burned": amount
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
