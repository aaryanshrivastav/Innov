# 🪙 IndiCoin Control Panel  

A full-stack App that lets users **mint IndiCoin using INR** and **burn IndiCoin to redeem INR in Bitcoin**.  
Built with **React (frontend)** and **FastAPI (backend)**, the system ensures a seamless and professional UI for interacting with the IndiCoin ecosystem.  

---

## 🚀 Features  

### Mint IndiCoin  
- Enter INR amount → calls `/mint` → returns:  
  - `hardlimit` (max IndiCoin available)  
  - `message` (confirmation or error)  

### Burn IndiCoin  
- Enter IndiCoin amount to burn → calls `/burn` → returns:  
  - `remainingIndi` (balance after burning)  
  - `btcValue` (equivalent BTC received)  
  - `transactionId` (for tracking)  
  - `inrConverted` (redeemed INR value)  

### Modern UI  
- Responsive React frontend  
- Sleek dark theme for professional look  
- Error/success feedback with toast alerts  

---

## 🛠️ Tech Stack  

### Frontend  
- React
- TailwindCSS (styling)  

### Backend  
- FastAPI (Python)  
- Pydantic for request/response models  

## ⚡ Getting Started  

### 1️⃣ Backend Setup  

```bash
pip install fastapi uvicorn pydantic
uvicorn app:app --reload --port 8000
API Endpoints:

POST /mint → Mint IndiCoin

POST /burn → Burn IndiCoin

npm install
npm start   


