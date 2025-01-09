import pandas as pd
import datetime
import mysql.connector
from _config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

# Connect to the database
mydb = mysql.connector.connect(
    host= DB_HOST,
    user= DB_USER,
    password= DB_PASSWORD,
    database= DB_NAME
)

mycursor = mydb.cursor()

# Get the current date and time
today = datetime.datetime.now()

# Define the time cutoff (5:30 PM)
cutoff_time = today.replace(hour=17, minute=30, second=0, microsecond=0)

# Determine the formatted date based on the time of day and weekday
if today < cutoff_time:
    # Before 5:30 PM
    if today.weekday() == 6:  # Sunday
        # If today is Sunday, set to Friday
        formatted_date = (today - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    elif today.weekday() == 0:  # Monday
        # If today is Monday, set to Friday
        formatted_date = (today - datetime.timedelta(days=3)).strftime("%Y-%m-%d")
    else:
        # Otherwise, set to yesterday
        formatted_date = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
else:
    # After 5:30 PM
    if today.weekday() == 5:  # Saturday
        formatted_date = (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    elif today.weekday() == 6:  # Sunday
        formatted_date = (today - datetime.timedelta(days=2)).strftime("%Y-%m-%d")
    else:
        # Otherwise, set to today
        formatted_date = today.strftime("%Y-%m-%d")

# Fetch bhavcopy data for yesterday
q1 = "SELECT * FROM bhavcopydata WHERE TRADE_DATE = %s"
mycursor.execute(q1, (formatted_date,))
results = mycursor.fetchall()

results = pd.DataFrame(results, columns=['UNIQUE_ID', 'SYMBOL', 'SERIES', 'TRADE_DATE', 'PREV_CLOSE', 'OPEN_PRICE', 'HIGH_PRICE', 'LOW_PRICE', 'LAST_PRICE', 'CLOSE_PRICE', 'AVG_PRICE', 'TTL_TRD_QNTY', 'TURNOVER_LACS', 'NO_OF_TRADES', 'DELIV_QTY', 'DELIV_PER', 'ISIN', 'COMMENTS'])

# Fetch all user ids
q_user_ids = "SELECT USER_ID FROM users"
mycursor.execute(q_user_ids)
user_ids = mycursor.fetchall()
user_ids = [user[0] for user in user_ids]  # Convert to a list of user IDs

# Iterate over all user IDs
for user_id in user_ids:
    # Fetch active triggers for the current user
    q2 = "SELECT * FROM active_triggers WHERE USER_ID = %s AND STATUS = 'ACTIVE'"
    mycursor.execute(q2, (user_id,))
    triggers = mycursor.fetchall()
    triggers = pd.DataFrame(triggers, columns=['USER_ID', 'TRIGGER_ID', 'SYMBOL', 'SERIES', 'LOP', 'BOP', 'DEVIATION', 'COMMENTS', 'STATUS'])

    # Add UNIQUE_ID to triggers for comparison with bhavcopydata
    if 'UNIQUE_ID' not in triggers.columns:
        triggers['UNIQUE_ID'] = triggers['TRIGGER_ID'].str.strip() + formatted_date
        triggers = triggers[['UNIQUE_ID'] + [col for col in triggers.columns if col != 'UNIQUE_ID']]
    
    # Perform the comparison and collect the results
    comparison_results = []
    for idx_triggers, trigger_row in triggers.iterrows():
        unique_id_trigger = trigger_row['UNIQUE_ID']
        matching_result_row = results[results['UNIQUE_ID'] == unique_id_trigger]
        # print(unique_id_trigger)
        # print(matching_result_row)
        if not matching_result_row.empty:
            lop = trigger_row['LOP']
            bop = trigger_row['BOP']
            low = matching_result_row['LOW_PRICE'].values[0]
            high = matching_result_row['HIGH_PRICE'].values[0]
<<<<<<< Updated upstream
<<<<<<< Updated upstream
            date = matching_result_row['TRADE_DATE'].values[0]
=======
            open = matching_result_row['OPEN_PRICE'].values[0]
            close = matching_result_row['CLOSE_PRICE'].values[0]
>>>>>>> Stashed changes
=======
            open = matching_result_row['OPEN_PRICE'].values[0]
            close = matching_result_row['CLOSE_PRICE'].values[0]
>>>>>>> Stashed changes
            deviation = trigger_row['DEVIATION']

            lop = lop * (1 + deviation / 100)
            bop = bop * (1 - deviation / 100)
            if pd.notna(lop) or pd.notna(bop):
                if lop is not None and bop is not None:
                    if low < lop and high > bop:
<<<<<<< Updated upstream
<<<<<<< Updated upstream
                        comparison_results.append(trigger_row.tolist() + [date, 'BOTH'])
                    elif high > bop:
                        comparison_results.append(trigger_row.tolist() + [date, 'BOP'])
                    elif low < lop:
                        comparison_results.append(trigger_row.tolist() + [date, 'LOP'])
                elif lop is None and bop is not None and high > bop:
                    comparison_results.append(trigger_row.tolist() + [date, 'BOP'])
                elif bop is None and lop is not None and low < lop:
                    comparison_results.append(trigger_row.tolist() + [date, 'LOP'])

    triggered_df = pd.DataFrame(comparison_results, columns=['UNIQUE_ID','USER_ID','TRIGGER_ID', 'SYMBOL', 'SERIES', 'LOP', 'BOP', 'DEVIATION','COMMENTS','STATUS','TRIGGER_DATE', 'TYPE'])

    # Insert the triggered results into previous_triggers and update the status in active_triggers
    for i in triggered_df.itertuples(index=False):
        # Insert into previous_triggers table
        q3 = "INSERT IGNORE INTO previous_triggers(UNIQUE_ID, USER_ID, SYMBOL, SERIES, LOP, BOP, DEVIATION, TRIGGER_DATE, TYPE, COMMENTS) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val1 = (i[0], i[1], i[3], i[4], i[5], i[6], i[7], i[10], i[11], i[8])  # Including COMMENTS
=======
                        comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date, today.strftime("%Y-%m-%d"), 'BOTH'])
                    elif high > bop:
                        comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date, today.strftime("%Y-%m-%d"), 'BOP'])
                    elif low < lop:
                        comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date, today.strftime("%Y-%m-%d"), 'LOP'])
                elif lop is None and bop is not None and high > bop:
                    comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date, today.strftime("%Y-%m-%d"), 'BOP'])
                elif bop is None and lop is not None and low < lop:
                    comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date, today.strftime("%Y-%m-%d"), 'LOP'])

    triggered_df = pd.DataFrame(comparison_results, columns=['UNIQUE_ID','USER_ID','TRIGGER_ID', 'SYMBOL', 'SERIES', 'HNI', 'LOP', 'BOP', 'DEVIATION','COMMENTS','STATUS','OPEN_PRICE', 'HIGH_PRICE', 'LOW_PRICE', 'CLOSE_PRICE','TRADE_DATE', 'TRIGGER_DATE', 'TYPE'])
    df_cleaned = triggered_df.fillna('')
    print('No of triggers find: ',triggered_df.size)

=======
                        comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date, today.strftime("%Y-%m-%d"), 'BOTH'])
                    elif high > bop:
                        comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date, today.strftime("%Y-%m-%d"), 'BOP'])
                    elif low < lop:
                        comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date, today.strftime("%Y-%m-%d"), 'LOP'])
                elif lop is None and bop is not None and high > bop:
                    comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date, today.strftime("%Y-%m-%d"), 'BOP'])
                elif bop is None and lop is not None and low < lop:
                    comparison_results.append(trigger_row.tolist() + [open, high, low, close, formatted_date, today.strftime("%Y-%m-%d"), 'LOP'])

    triggered_df = pd.DataFrame(comparison_results, columns=['UNIQUE_ID','USER_ID','TRIGGER_ID', 'SYMBOL', 'SERIES', 'HNI', 'LOP', 'BOP', 'DEVIATION','COMMENTS','STATUS','OPEN_PRICE', 'HIGH_PRICE', 'LOW_PRICE', 'CLOSE_PRICE','TRADE_DATE', 'TRIGGER_DATE', 'TYPE'])
    df_cleaned = triggered_df.fillna('')
    print('No of triggers find: ',triggered_df.size)

>>>>>>> Stashed changes
    # Insert the triggered results into alerts_table and update the status in active_triggers
    for i in df_cleaned.itertuples(index=False):
        # Insert into alerts_table table
        q3 = "INSERT IGNORE INTO alerts_table(UNIQUE_ID, USER_ID, SYMBOL, SERIES, HNI, LOP, BOP, DEVIATION, COMMENTS, OPEN_PRICE, HIGH_PRICE, LOW_PRICE, CLOSE_PRICE, TRADE_DATE, TRIGGER_DATE, TYPE) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        val1 = (i[0], i[1], i[3], i[4], i[5], i[6], i[7], i[8], i[9], i[11], i[12], i[13], i[14], i[15], i[16], i[17])  # Including COMMENTS
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
        mycursor.execute(q3, val1)

        # Update status to 'Inactive' in active_triggers table
        q4 = "UPDATE active_triggers SET STATUS = 'INACTIVE' WHERE TRIGGER_ID = %s and USER_ID = %s"
        val2 = (i[2], i[1])
        mycursor.execute(q4, val2)

        # Commit changes to the database
        mydb.commit()

# Close the cursor and database connection
mycursor.close()
mydb.close()