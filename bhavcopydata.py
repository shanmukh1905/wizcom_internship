import datetime
import os
import requests
import pandas as pd
import mysql.connector
from _config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER
<<<<<<< Updated upstream

import datetime
=======
>>>>>>> Stashed changes

# Get the current date and time
today = datetime.datetime.now()

# Define the time cutoff (5:30 PM)
cutoff_time = today.replace(hour=17, minute=30, second=0, microsecond=0)

# Determine the formatted date based on the time of day and weekday
if today < cutoff_time:
    # Before 5:30 PM
    if today.weekday() == 6:  # Sunday
        # If today is Sunday, set to Friday
        formatted_date = (today - datetime.timedelta(days=2)).strftime("%d%m%Y")
    elif today.weekday() == 0:  # Monday
        # If today is Monday, set to Friday
        formatted_date = (today - datetime.timedelta(days=3)).strftime("%d%m%Y")
    else:
        # Otherwise, set to yesterday
        formatted_date = (today - datetime.timedelta(days=1)).strftime("%d%m%Y")
else:
    # After 5:30 PM
    if today.weekday() == 5:# Saturday
        formatted_date = (today - datetime.timedelta(days=1)).strftime("%d%m%Y")
    elif today.weekday() == 6:  # Sunday
        formatted_date = (today - datetime.timedelta(days=2)).strftime("%d%m%Y")
    else:
        # Otherwise, set to today
        formatted_date = today.strftime("%d%m%Y")

# Set the URL for fetching data
url = f"https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{formatted_date}.csv"

# Set the headers for the request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive'
}

# Folder to save the CSV file
folder_path = "bhavcsvs"

# Create folder if it does not exist
if not os.path.exists(folder_path):
    os.makedirs(folder_path)
    print(f"Folder '{folder_path}' created")

# Set the path for the file
file_path = f"{folder_path}/sec_bhavdata_full_{formatted_date}.csv"

# Fetch the CSV file
response = requests.get(url, headers=headers)

# Check if the request was successful
if response.status_code == 200:
    print("File fetched successfully")
    with open(file_path, 'wb') as file:
        file.write(response.content)
else:
    print(f"Failed to fetch file. Status code: {response.status_code}. Exiting script.")
    exit(1)  # Exit the script if the file is not fetched

# Load the CSV data into a DataFrame
df = pd.read_csv(file_path)
df = pd.DataFrame(df)

# Clean the ' DATE1' column
df[' DATE1'] = df[' DATE1'].str.strip()
df[' DATE1'] = pd.to_datetime(df[' DATE1'], format='%d-%b-%Y')
df[' DATE1'] = df[' DATE1'].dt.strftime('%Y-%m-%d')

# Create the UNIQUE_ID column if not already present
if 'UNIQUE_ID' not in df.columns:
    df['UNIQUE_ID'] = df.iloc[:, 0].str.strip() + df.iloc[:, 1].str.strip() + df.iloc[:, 2].str.strip()
    df = df[['UNIQUE_ID'] + [col for col in df.columns if col != 'UNIQUE_ID']]

# Clean the 'DELIV_QTY' and 'DELIV_PER' columns
df[' DELIV_QTY'] = df[' DELIV_QTY'].apply(lambda x: None if isinstance(x, str) and x.strip() == '-' else x)
df[' DELIV_PER'] = df[' DELIV_PER'].apply(lambda x: None if isinstance(x, str) and x.strip() == '-' else x)

# Connect to MySQL database
mydb = mysql.connector.connect(
    host= DB_HOST,
    user= DB_USER,
    password= DB_PASSWORD,
    database= DB_NAME
)

mycursor = mydb.cursor()

# Insert data into the MySQL database
for i in df.itertuples(index=False):
    sql = """
    INSERT IGNORE INTO bhavcopydata(
        UNIQUE_ID, SYMBOL, SERIES, TRADE_DATE, PREV_CLOSE, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, LAST_PRICE,
        CLOSE_PRICE, AVG_PRICE, TTL_TRD_QNTY, TURNOVER_LACS, NO_OF_TRADES, DELIV_QTY, DELIV_PER
    ) VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)
    """
    val = (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11], i[12], i[13], i[14], i[15])
    mycursor.execute(sql, val)
    mydb.commit()

# Close database connections
mycursor.close()
mydb.close()