import dotenv
import os
import requests
import time
from pymongo import MongoClient
from get_wallets_from_csv import get_wallets_from_csv
from save_as_csv_file import export_mongo_to_csv
dotenv.load_dotenv()
CIELO_API_KEY=os.getenv("CIELO_API_KEY")


def save_pnl_and_winrate_to_excel():
  # Function to get price based on wallet address
  def get_data_from_cielo(wallet_address, date):
    cielo_url = f"https://feed-api.cielo.finance/api/v1/{wallet_address}/pnl/total-stats?timeframe={date}d"  # URL to check wallet stats using Cielo API
    cielo_headers = {
      "accept": "application/json",
      "X-API-KEY": CIELO_API_KEY  # Set headers with Cielo API key
    }
    
    cielo_response = requests.get(cielo_url, headers=cielo_headers)  # Send GET request to Cielo API
    print(f"Checking {wallet_address}... => cielo response status code is {cielo_response.status_code}")
    
    if cielo_response.status_code != 200:
      time.sleep(5)
      cielo_response = requests.get(cielo_url, headers=cielo_headers)
      if cielo_response.status_code != 200:
        data = {
          "realized_profit": 0, 
          "unrealized_profit": 0, 
          "combined_profit": 0,
          "realized_roi": 0, 
          "unrealized_roi": 0, 
          "combined_roi": 0,
          "winrate": 0, 
          "tokens_traded": 0, 
          "average_traded_time": 0, 
        }
        return data
      
    cielo_data = cielo_response.json()
    print(cielo_data)
    data = {
      "realized_profit": cielo_data['data']['realized_pnl_usd'], 
      "unrealized_profit": cielo_data['data']['unrealized_pnl_usd'], 
      "combined_profit": cielo_data['data']['combined_pnl_usd'],
      "realized_roi": cielo_data['data']['realized_roi_percentage'], 
      "unrealized_roi": cielo_data['data']['unrealized_roi_percentage'], 
      "combined_roi": cielo_data['data']['combined_roi_percentage'],
      "winrate": cielo_data['data']['winrate'], 
      "tokens_traded": cielo_data['data']['tokens_traded'], 
      "average_traded_time": cielo_data['data']['average_holding_time'], 
    }
    return data
    
  mongo_client = MongoClient("mongodb+srv://vanguard951105:F0Y7B0MtjvH1OFbL@cluster0.haemz.mongodb.net/") 
  db = mongo_client["Dexscreener"]  # Select the database named "Dexscreener"
  collection = db["solana_track"]  # Select the collection named "wallet_data"
  collection.delete_many({})  # Clear old wallet information from the collection

  wallets = get_wallets_from_csv()
  for wallet in wallets:
    document = {
      "wallet_address": wallet,
      "realized_profit": [],
      "unrealized_profit": [], 
      "combined_profit":[],
      "realized_roi": [], 
      "unrealized_roi": [], 
      "combined_roi":[],
      "winrate": [], 
      "tokens_traded": [], 
      "average_traded_time": [],
      
    }
    for date in [1, 7, 30]:
      data = get_data_from_cielo(wallet, date)
      field = f"{date}D"
      document["realized_profit"].append({field: data["realized_profit"]})
      document["unrealized_profit"].append({field: data["unrealized_profit"]})
      document["combined_profit"].append({field: data["combined_profit"]})
      document["realized_roi"].append({field: data["realized_roi"]})
      document["unrealized_roi"].append({field: data["unrealized_roi"]})
      document["combined_roi"].append({field: data["combined_roi"]})
      document["winrate"].append({field: data["winrate"]})
      document["tokens_traded"].append({field: data["tokens_traded"]})
      document["average_traded_time"].append({field: data["average_traded_time"]})

    collection.insert_one(document)  # Insert the document into the collection
    print(f"{document} has been saved to database successfully")

while True:  # Infinite loop to repeatedly execute the following actions
  save_pnl_and_winrate_to_excel()
  export_mongo_to_csv() # Export csv file to result directory 
  time.sleep(86400)  # Pause execution for 86400 seconds (a day) before repeating
  print(f"Will update after a day...")