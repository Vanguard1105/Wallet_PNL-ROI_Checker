import pandas as pd

def get_wallets_from_csv():
    file_path = 'target.csv'  # Replace with your CSV file path
    column_name = 'wallet_address'  # Replace with the actual column name in your CSV
    df = pd.read_csv(file_path, usecols=[column_name])
    wallets = df[column_name].tolist()
    return wallets