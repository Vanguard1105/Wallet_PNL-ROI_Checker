import pandas as pd
from pymongo import MongoClient
from datetime import datetime
import csv
import os

def export_mongo_to_csv():
    # Connect to MongoDB
    mongo_client = MongoClient("mongodb+srv://vanguard951105:F0Y7B0MtjvH1OFbL@cluster0.haemz.mongodb.net/")
    
    # Access the specified database and collection
    db = mongo_client["Dexscreener"]
    collection = db["solana_track"]
    
    # Fetch all documents from the collection
    cursor = collection.find()
    
    # Convert cursor to a list of documents
    documents = list(cursor)
    fieldnames = ['wallet_address', 
                  're_profit(7D)', 
                  'un_profit(7D)', 
                  'co_profit(7D)', 
                  're_roi(7D)', 
                  'un_roi(7D)', 
                  'co_roi(7D)', 
                  'winrate(7D)',
                  'traded_token(7D)', 
                  'avg_traded_time',
                  ]
    result = []
    for data in documents:
        new_data = {
            'wallet_address': data['wallet_address'], 
            're_profit(7D)': data['realized_profit'][0]['7D'],
            'un_profit(7D)': data['unrealized_profit'][0]['7D'], 
            'co_profit(7D)': data['combined_profit'][0]['7D'], 
            're_roi(7D)': data['realized_roi'][0]['7D'], 
            'un_roi(7D)': data['unrealized_roi'][0]['7D'], 
            'co_roi(7D)': data['combined_roi'][0]['7D'], 
            'winrate(7D)': data['winrate'][0]['7D'],
            'traded_token(7D)': data['tokens_traded'][0]['7D'], 
            'avg_traded_time': data['average_traded_time'][0]['7D'],
        }
        result.append(new_data)

    # Get today's date and format it as YYYY-MM-DD
    today_date = datetime.now().strftime("%Y-%m-%d")
    
    # Define the output directory and file name
    output_directory = "result"
    output_file_path = os.path.join(output_directory, f"{today_date}.csv")

    with open(output_file_path, mode='w', newline='') as outfile:
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        
        writer.writeheader()  # Write header row
        writer.writerows(result)  # Write multiple rows of data

    print(f"Data has been written to {output_file_path}.")