import sys
import os
import requests
import pandas as pd
import mysql.connector
from datetime import datetime
from _config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

# Set display options to show all rows and columns 
pd.set_option('display.max_rows', None) 
pd.set_option('display.max_columns', None)

log_filepath = sys.argv[1]
# Open the log file in append mode 
log_file = open(log_filepath, 'a')
 
# Redirect stdout and stderr to the log file 
sys.stdout = log_file 
sys.stderr = log_file

today = datetime.now()
# Function to parse date argument
def parse_date(user_date):
    try:
        date_obj = datetime.strptime(user_date, '%Y-%m-%d')
        return date_obj.strftime("%d%m%Y")
    except ValueError:
        print("Invalid date format. Please use YYYY-MM-DD.")
        sys.exit(1)

# Function to connect to the MySQL database
def connect_to_db():
    return mysql.connector.connect(
        host= DB_HOST,
        user= DB_USER,
        password= DB_PASSWORD,
        database= DB_NAME
    )

# Function to create the folder for saving CSV if it doesn't exist
def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Folder '{folder_path}' created")

# Function to fetch CSV data from NSE
def fetch_csv_data(url, file_path):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        print("File fetched successfully")
        with open(file_path, 'wb') as file:
            file.write(response.content)
    else:
        print(f"Failed to fetch file. Status code: {response.status_code}. Exiting script.")
        sys.exit(1)

# Function to load and clean the CSV data
def load_and_clean_csv(file_path):
    df = pd.read_csv(file_path)
    df[' DATE1'] = df[' DATE1'].str.strip()
    df[' DATE1'] = pd.to_datetime(df[' DATE1'], format='%d-%b-%Y')
    df[' DATE1'] = df[' DATE1'].dt.strftime('%Y-%m-%d')

    # Add UNIQUE_ID if it doesn't exist
    if 'UNIQUE_ID' not in df.columns:
        df['UNIQUE_ID'] = df.iloc[:, 0].str.strip() + df.iloc[:, 1].str.strip() + df.iloc[:, 2].str.strip()
        df = df[['UNIQUE_ID'] + [col for col in df.columns if col != 'UNIQUE_ID']]

    # Clean 'DELIV_QTY' and 'DELIV_PER' columns
    df[' DELIV_QTY'] = df[' DELIV_QTY'].apply(lambda x: None if isinstance(x, str) and x.strip() == '-' else x)
    df[' DELIV_PER'] = df[' DELIV_PER'].apply(lambda x: None if isinstance(x, str) and x.strip() == '-' else x)

    return df

# Function to insert data into the MySQL database
def insert_data_into_db(df, mycursor):
    for i in df.itertuples(index=False):
        sql = """
        INSERT IGNORE INTO bhavcopydata(
            UNIQUE_ID, SYMBOL, SERIES, TRADE_DATE, PREV_CLOSE, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, LAST_PRICE,
            CLOSE_PRICE, AVG_PRICE, TTL_TRD_QNTY, TURNOVER_LACS, NO_OF_TRADES, DELIV_QTY, DELIV_PER
        ) VALUES (%s, %s, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)
        """
        val = (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[10], i[11], i[12], i[13], i[14], i[15])
        mycursor.execute(sql, val)

# Function to fetch active triggers from the database for a specific user
def fetch_active_triggers(user_id, mycursor):
    q2 = "SELECT * FROM active_triggers WHERE USER_ID = %s AND STATUS = 'ACTIVE'"
    mycursor.execute(q2, (user_id,))
    triggers = mycursor.fetchall()
    return pd.DataFrame(triggers, columns=['USER_ID', 'TRIGGER_ID', 'SYMBOL', 'SERIES', 'HNI', 'LOP', 'BOP', 'DEVIATION', 'COMMENTS', 'STATUS'])

# Function to compare and trigger results
def compare_triggers(triggers, results, formatted_date_new):
    comparison_results = []
    for idx_triggers, trigger_row in triggers.iterrows():
        unique_id_trigger = trigger_row['UNIQUE_ID']
        matching_result_row = results[results['UNIQUE_ID'] == unique_id_trigger]
        if not matching_result_row.empty:
            lop = trigger_row['LOP']
            bop = trigger_row['BOP']
            low = matching_result_row['LOW_PRICE'].values[0]
            high = matching_result_row['HIGH_PRICE'].values[0]
            open = matching_result_row['OPEN_PRICE'].values[0]
            close = matching_result_row['CLOSE_PRICE'].values[0]
            deviation = trigger_row['DEVIATION']
            if lop is not None:
                lop = lop * (1 + deviation / 100)
            if bop is not None:
                bop = bop * (1 - deviation / 100)

            if pd.notna(lop) or pd.notna(bop):
                if lop is not None and bop is not None:
                    if low < lop and high > bop:
                        comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date_new, today.strftime("%Y-%m-%d"), 'BOTH'])
                    elif high > bop:
                        comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date_new, today.strftime("%Y-%m-%d"), 'BOP'])
                    elif low < lop:
                        comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date_new, today.strftime("%Y-%m-%d"), 'LOP'])
                elif lop is None and bop is not None and high > bop:
                    comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date_new, today.strftime("%Y-%m-%d"), 'BOP'])
                elif bop is None and lop is not None and low < lop:
                    comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date_new, today.strftime("%Y-%m-%d"), 'LOP'])
    return pd.DataFrame(comparison_results, columns=['UNIQUE_ID','USER_ID','TRIGGER_ID', 'SYMBOL', 'SERIES', 'HNI', 'LOP', 'BOP', 'DEVIATION','COMMENTS','STATUS','OPEN_PRICE', 'HIGH_PRICE', 'LOW_PRICE', 'CLOSE_PRICE','TRADE_DATE', 'TRIGGER_DATE', 'TYPE'])

# Function to update the active and previous triggers in the database
def update_triggers(triggered_df, mycursor, mydb):
    # Replace NaN values with blank (empty strings) 
    df_cleaned = triggered_df.fillna('')
    # print(triggered_d)
    for i in df_cleaned.itertuples(index=False):
        # Insert into alerts_table table
        q3 = "INSERT IGNORE INTO alerts_table(UNIQUE_ID, USER_ID, SYMBOL, SERIES, HNI, LOP, BOP, DEVIATION, COMMENTS, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, TRADE_DATE, TRIGGER_DATE, TYPE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val1 = (i[0], i[1], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[11], i[12], i[13], i[14], i[15], i[16], i[17])  # Including COMMENTS
        mycursor.execute(q3, val1)

        # Commit changes to the database
        mydb.commit()

# Main function to execute the workflow
def main():
    # Validate arguments
    if len(sys.argv) != 4:
        print("Usage: python helper.py <log_file_name> <user_id> <date>")
        sys.exit(1)

    user_id = sys.argv[2]  # Get user_id from command-line argument
    user_date = sys.argv[3]

    formatted_date = parse_date(user_date)
    formatted_date_new = datetime.strptime(user_date, '%Y-%m-%d').strftime('%Y-%m-%d')

    # Connect to MySQL
    mydb = connect_to_db()
    mycursor = mydb.cursor()

    # Set folder path and create folder if necessary
    folder_path = "bhavcsvs"
    create_folder(folder_path)

    # Fetch CSV data from the NSE
    url = f"https://nsearchives.nseindia.com/products/content/sec_bhavdata_full_{formatted_date}.csv"
    file_path = f"{folder_path}/sec_bhavdata_full_{formatted_date}.csv"
    fetch_csv_data(url, file_path)

    # Load and clean CSV data
    df = load_and_clean_csv(file_path)

    # Insert cleaned data into the database
    insert_data_into_db(df, mycursor)
    mydb.commit()

    # Query the results from the database for the specific user_id
    q1 = "SELECT * FROM bhavcopydata WHERE TRADE_DATE = %s"
    mycursor.execute(q1, (formatted_date_new,))
    results = mycursor.fetchall()
    results = pd.DataFrame(results, columns=['id','UNIQUE_ID', 'SYMBOL', 'SERIES', 'TRADE_DATE', 'PREV_CLOSE', 'OPEN_PRICE', 'HIGH_PRICE', 'LOW_PRICE', 'LAST_PRICE', 'CLOSE_PRICE', 'AVG_PRICE', 'TTL_TRD_QNTY', 'TURNOVER_LACS', 'NO_OF_TRADES', 'DELIV_QTY', 'DELIV_PER', 'ISIN', 'COMMENTS'])

    # Fetch active triggers for the specific user_id
    print('Fetching active triggers from the database for a specific user_id: '+ user_id)
    triggers = fetch_active_triggers(user_id, mycursor)
    if 'UNIQUE_ID' not in triggers.columns:
        triggers['UNIQUE_ID'] = triggers['TRIGGER_ID'].str.strip() + formatted_date_new
        triggers = triggers[['UNIQUE_ID'] + [col for col in triggers.columns if col != 'UNIQUE_ID']]

    triggered_df = compare_triggers(triggers, results, formatted_date_new)
    update_triggers(triggered_df, mycursor, mydb)

    # Close the cursor and database connection
    mycursor.close()
    mydb.close()

if __name__ == '__main__':
    main()
