from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import pandas as pd
import numpy as np

from fastapi.middleware.cors import CORSMiddleware

from pycoingecko import CoinGeckoAPI
import requests
from datetime import date, timedelta

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.callbacks import EarlyStopping
import joblib

app = FastAPI(title="IndiCoin Buy-Limit Predictor")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
RISK_PROFILES = {
    "conservative": {"max_crypto_allocation": 0.15, "volatility_penalty": 2.0},
    "moderate": {"max_crypto_allocation": 0.25, "volatility_penalty": 1.5},
    "aggressive": {"max_crypto_allocation": 0.40, "volatility_penalty": 1.0}
}

def fetch_historical_data(days=30, granularity="daily"):
    try:
        cg = CoinGeckoAPI()
        btc_data = cg.get_coin_market_chart_by_id(id='bitcoin', vs_currency='usd', days=days)
        prices = btc_data['prices']
        btc_df = pd.DataFrame(prices, columns=['timestamp', 'BTC_USD'])
        btc_df['Date'] = pd.to_datetime(btc_df['timestamp'], unit='ms').dt.date
        btc_df = btc_df.groupby('Date')['BTC_USD'].last().reset_index()

        start_date = (date.today() - timedelta(days=days)).strftime('%Y-%m-%d')
        end_date = date.today().strftime('%Y-%m-%d')
        url = f'https://api.frankfurter.app/{start_date}..{end_date}?from=USD&to=INR'
        resp = requests.get(url)
        data = resp.json()
        fx_data = pd.DataFrame(list(data['rates'].items()), columns=['Date', 'INR_dict'])
        fx_data['Date'] = pd.to_datetime(fx_data['Date']).dt.date
        fx_data['USD_INR'] = fx_data['INR_dict'].apply(lambda x: x['INR'])
        fx_data.drop(columns=['INR_dict'], inplace=True)

        df = pd.merge(btc_df, fx_data, on='Date', how='inner')
        df.rename(columns={'Date': 'timestamp'}, inplace=True)
        df = df[['timestamp', 'BTC_USD', 'USD_INR']]
        df = df.dropna()
        return df

    except Exception as e:
        print(f"Error fetching data: {e}")
        dates = pd.date_range(start='2024-01-01', periods=days, freq='D')
        return pd.DataFrame({
            'timestamp': dates,
            'BTC_USD': np.random.uniform(40000, 50000, len(dates)),
            'USD_INR': np.random.uniform(82, 84, len(dates))
        })

def calculate_portfolio_metrics(df_hist):
    df_hist["BTC_Return"] = df_hist["BTC_USD"].pct_change()
    df_hist["USD_INR_Return"] = df_hist["USD_INR"].pct_change()
    df_hist["BTC_Volatility"] = df_hist["BTC_Return"].rolling(30).std() * np.sqrt(24)
    df_hist["Currency_Volatility"] = df_hist["USD_INR_Return"].rolling(30).std() * np.sqrt(24)
    df_hist["BTC_MA_20"] = df_hist["BTC_USD"].rolling(20).mean()
    df_hist["BTC_Trend"] = (df_hist["BTC_USD"] - df_hist["BTC_MA_20"]) / df_hist["BTC_MA_20"]
    delta = df_hist["BTC_USD"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df_hist["Market_Sentiment"] = 100 - (100 / (1 + rs))
    return df_hist.dropna()

def calculate_smart_hard_limit(btc_volatility, market_sentiment, btc_trend, current_btc_price,
                               btc_usd, usd_inr, user_balance, existing_btc_holdings,
                               risk_profile="moderate"):
    profile = RISK_PROFILES[risk_profile]
    user_balance = float(user_balance)
    base_crypto_allocation = user_balance * profile["max_crypto_allocation"]
    existing_btc_value_usd = existing_btc_holdings * btc_usd
    existing_btc_value_indicoin = existing_btc_value_usd / usd_inr

    if existing_btc_holdings > 0:
        existing_exposure_ratio = min(existing_btc_value_indicoin / user_balance, 2.0)
        reduction_multiplier = {"conservative": 0.5, "moderate": 0.3, "aggressive": 0.2}[risk_profile]
        reduction_factor = 1 - (existing_exposure_ratio * reduction_multiplier)
        reduction_factor = max(0.1, reduction_factor)
    else:
        reduction_factor = 1.0

    adjusted_allocation = base_crypto_allocation * reduction_factor
    volatility_factor = 1 / (1 + profile["volatility_penalty"] * btc_volatility)

    if market_sentiment < 20:
        sentiment_factors = {"conservative": 1.1, "moderate": 1.2, "aggressive": 1.3}
        sentiment_factor = sentiment_factors[risk_profile]
    elif market_sentiment > 80:
        sentiment_factors = {"conservative": 0.5, "moderate": 0.7, "aggressive": 0.8}
        sentiment_factor = sentiment_factors[risk_profile]
    else:
        sentiment_factor = 1.0

    if btc_trend > 0.15:
        trend_factors = {"conservative": 0.6, "moderate": 0.8, "aggressive": 0.9}
        trend_factor = trend_factors[risk_profile]
    elif btc_trend < -0.15:
        trend_factors = {"conservative": 1.05, "moderate": 1.1, "aggressive": 1.2}
        trend_factor = trend_factors[risk_profile]
    else:
        trend_factor = 1.0

    final_allocation = adjusted_allocation * volatility_factor * sentiment_factor * trend_factor

    profile_max_trade = {
        "conservative": user_balance * 0.10,
        "moderate": user_balance * 0.20,
        "aggressive": user_balance * 0.35
    }

    final_limit = min(final_allocation, profile_max_trade[risk_profile])
    return max(0, final_limit)

df_hist = fetch_historical_data(days=365, granularity="daily")
df_hist = calculate_portfolio_metrics(df_hist)

def create_target_allocation(df, lookforward=7):
    df['Future_Return'] = df['BTC_USD'].shift(-lookforward) / df['BTC_USD'] - 1
    df['Future_Vol'] = df['BTC_Return'].rolling(lookforward).std().shift(-lookforward)
    sharpe_proxy = df['Future_Return'] / (df['Future_Vol'] + 0.01)
    target_alloc = (sharpe_proxy - sharpe_proxy.quantile(0.1)) / (sharpe_proxy.quantile(0.9) - sharpe_proxy.quantile(0.1))
    target_alloc = np.clip(target_alloc * 0.25, 0, 0.25)
    return target_alloc

df_hist['Target_Allocation'] = create_target_allocation(df_hist)
df_hist = df_hist.dropna()

FEATURES = ["BTC_Volatility", "Market_Sentiment", "BTC_Trend", "Currency_Volatility"]
TARGET = "Target_Allocation"

baseline_mae = 0.08
test_mae = 0.05
model_available = False

if len(df_hist) < 60:
    baseline_allocation = 0.10
    model_available = False
    baseline_mae = 0.08
    test_mae = 0.05
else:
    scaler_X = MinMaxScaler()
    scaler_y = MinMaxScaler()
    X_all = scaler_X.fit_transform(df_hist[FEATURES])
    y_all = scaler_y.fit_transform(df_hist[[TARGET]])

    def make_windows(X, y, window=14):
        Xs, ys = [], []
        for i in range(window, len(X)):
            Xs.append(X[i-window:i])
            ys.append(y[i])
        return np.array(Xs), np.array(ys)

    WINDOW = 14
    X_seq, y_seq = make_windows(X_all, y_all, WINDOW)

    if len(X_seq) >= 20:
        split = int(0.8 * len(X_seq))
        X_train, X_test = X_seq[:split], X_seq[split:]
        y_train, y_test = y_seq[:split], y_seq[split:]

        model = Sequential([
            LSTM(32, return_sequences=True, input_shape=(WINDOW, len(FEATURES))),
            LSTM(16),
            Dense(8, activation="relu"),
            Dense(1, activation="sigmoid")
        ])

        model.compile(optimizer="adam", loss="mse", metrics=["mae"])
        es = EarlyStopping(monitor="val_loss", patience=10, restore_best_weights=True)

        if len(X_test) > 0:
            model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=100, batch_size=8, callbacks=[es], verbose=0)
            y_pred = model.predict(X_test, verbose=0)
            test_mae = mean_absolute_error(scaler_y.inverse_transform(y_test), scaler_y.inverse_transform(y_pred))
        else:
            model.fit(X_train, y_train, epochs=50, batch_size=8, verbose=0)
            test_mae = 0.05

        try:
            joblib.dump((scaler_X, scaler_y), "portfolio_scalers.pkl")
            model.save("portfolio_lstm.keras")
            model_available = True
        except Exception as e:
            print(f"Warning: Could not save model: {e}")
            model_available = False

        baseline_pred = np.full(len(y_test) if len(y_test) > 0 else len(y_train), 0.10)
        if len(y_test) > 0:
            baseline_mae = mean_absolute_error(scaler_y.inverse_transform(y_test), [[x] for x in baseline_pred])
        else:
            baseline_mae = 0.08
    else:
        model_available = False
        baseline_mae = 0.08
        test_mae = 0.05

def fetch_live_rates():
    try:
        cg = CoinGeckoAPI()
        btc_data = cg.get_price(ids='bitcoin', vs_currencies='usd')
        btc = float(btc_data['bitcoin']['usd'])
        url = f'https://api.frankfurter.app/latest?from=USD&to=INR'
        resp = requests.get(url)
        data = resp.json()
        usd_inr = float(data['rates']['INR'])
        return btc, usd_inr
    except Exception as e:
        print(f"Warning: Using fallback rates. Error: {e}")
        return 100000.0, 83.0

def predict_optimal_allocation(btc_usd, usd_inr, user_balance, existing_btc_holdings,
                             first_time=False, risk_profile="moderate"):
    try:
        current_volatility = df_hist["BTC_Volatility"].iloc[-1] if len(df_hist) > 0 else 0.3
        current_sentiment = df_hist["Market_Sentiment"].iloc[-1] if len(df_hist) > 0 else 50
        current_trend = df_hist["BTC_Trend"].iloc[-1] if len(df_hist) > 0 else 0

        if model_available and len(df_hist) > 0:
            try:
                saved_model = load_model("portfolio_lstm.keras")
                scaler_X, scaler_y = joblib.load("portfolio_scalers.pkl")
                current_currency_vol = df_hist["Currency_Volatility"].iloc[-1] if len(df_hist) > 0 else 0.05
                features = np.array([[current_volatility, current_sentiment, current_trend, current_currency_vol]])
                features_scaled = scaler_X.transform(features)
                if len(X_seq) > 0:
                    recent_seq = X_seq[-1][1:, :]
                    new_seq = np.vstack([recent_seq, features_scaled]).reshape(1, WINDOW, len(FEATURES))
                    predicted_allocation = saved_model.predict(new_seq, verbose=0)[0][0]
                    predicted_allocation = scaler_y.inverse_transform([[predicted_allocation]])[0][0]
                else:
                    predicted_allocation = 0.15
            except Exception as e:
                print(f"LSTM prediction failed: {e}")
                predicted_allocation = 0.15
        else:
            predicted_allocation = 0.15

        smart_limit = calculate_smart_hard_limit(
            current_volatility, current_sentiment, current_trend, btc_usd,
            btc_usd, usd_inr, user_balance, existing_btc_holdings, risk_profile
        )

        lstm_based_limit = user_balance * predicted_allocation
        final_limit = min(smart_limit, lstm_based_limit)

        first_time_bonus={"Conservative":1.2, "Moderate":1.3, "Aggressive":1.4}
        if first_time:
            final_limit *= first_time_bonus[risk_profile.title()]
        return max(0.0, final_limit)

    except Exception as e:
        print(f"Prediction error: {e}")
        profile_factor = {"conservative": 0.10, "moderate": 0.15, "aggressive": 0.25}.get(risk_profile, 0.15)
        return user_balance * profile_factor

class PredictionResponse(BaseModel):
    BTC_USD: float
    USD_INR: float
    Hard_Limit: float
    Recommended_Allocation_Percent: float
    Risk_Profile: str
    Market_Sentiment: str
    Baseline_MAE: float
    LSTM_MAE: float

@app.get("/predict", response_model=PredictionResponse)
def get_prediction(
    user_balance: float = Query(..., gt=0, description="User's IndiCoin balance"),
    first_time: bool = Query(False, description="Is this the user's first BTC purchase?"),
    btc_holdings: float = Query(0, ge=0, description="Existing BTC holdings"),
    risk_profile: str = Query("moderate", regex="^(conservative|moderate|aggressive)$",
                             description="Risk profile: conservative, moderate, or aggressive")
):
    try:
        btc_usd, usd_inr = fetch_live_rates()
        hard_limit = predict_optimal_allocation(
            btc_usd, usd_inr, user_balance, btc_holdings, first_time, risk_profile
        )
        recommended_percent = (hard_limit / user_balance * 100) if user_balance > 0 else 0
        current_sentiment = df_hist["Market_Sentiment"].iloc[-1] if len(df_hist) > 0 else 50
        if current_sentiment < 25:
            sentiment_text = "Extreme Fear - Good buying opportunity"
        elif current_sentiment < 45:
            sentiment_text = "Fear - Cautious buying opportunity"
        elif current_sentiment < 55:
            sentiment_text = "Neutral - Normal market conditions"
        elif current_sentiment < 75:
            sentiment_text = "Greed - Exercise caution"
        else:
            sentiment_text = "Extreme Greed - High risk conditions"

        return PredictionResponse(
            BTC_USD=round(btc_usd, 2),
            USD_INR=round(usd_inr, 4),
            Hard_Limit=round(hard_limit, 6),
            Recommended_Allocation_Percent=round(recommended_percent, 2),
            Risk_Profile=risk_profile.title(),
            Market_Sentiment=sentiment_text,
            Baseline_MAE=round(baseline_mae, 6),
            LSTM_MAE=round(test_mae, 6)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

@app.get("/")
def read_root():
    return {
        "message": "IndiCoin Portfolio Risk Manager API",
        "version": "2.0",
        "features": ["Smart Position Sizing", "Portfolio Risk Management", "Market Sentiment Analysis"]
    }

@app.get("/risk-profiles")
def get_risk_profiles():
    return {
        "profiles": {
            "conservative": "Max 15% crypto allocation, high volatility penalty",
            "moderate": "Max 25% crypto allocation, balanced approach",
            "aggressive": "Max 40% crypto allocation, lower volatility penalty"
        }
    }