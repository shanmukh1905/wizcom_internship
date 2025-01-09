import sys
import pandas as pd
import mysql.connector
from _config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

# Function to process the file and user ID
def process_file(file_path, user_id):
    # Step 1: Read the Excel file using pandas
    try:
        df = pd.read_excel(file_path)
    except Exception as e:
        return f"Error reading the Excel file: {str(e)}"
    
    # Step 2: Check if 'TRIGGER_ID' exists, if not, create it
    if 'TRIGGER_ID' not in df.columns:
        df['TRIGGER_ID'] = df.iloc[:, 0].str.strip() + df.iloc[:, 1].str.strip()  # Assuming 1st and 2nd columns are SYMBOL and SERIES
    
    # Rearranging columns to have 'TRIGGER_ID' as the first column
    df = df[['TRIGGER_ID'] + [col for col in df.columns if col != 'TRIGGER_ID']]
    
    # Step 3: Connect to MySQL database
    try:
        mydb = mysql.connector.connect(
            host= DB_HOST,
            user= DB_USER,
            password= DB_PASSWORD,
            database= DB_NAME

        )
        mycursor = mydb.cursor()
    except mysql.connector.Error as err:
        return f"Error connecting to MySQL: {err}"
    
    # Step 4: Insert data into MySQL
    for i in df.itertuples(index=False):
        sql = """
        INSERT INTO active_triggers 
        (USER_ID, TRIGGER_ID, SYMBOL, SERIES, HNI, LOP, BOP, DEVIATION, COMMENTS, STATUS) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE 
        USER_ID = VALUES(USER_ID), 
        SYMBOL = VALUES(SYMBOL), 
        SERIES = VALUES(SERIES), 
        HNI = VALUES(HNI), 
        LOP = VALUES(LOP), 
        BOP = VALUES(BOP), 
        DEVIATION = VALUES(DEVIATION), 
        COMMENTS = VALUES(COMMENTS), 
        STATUS = VALUES(STATUS)
        """
        val = (user_id, i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8])
        try:
            mycursor.execute(sql, val)
            mydb.commit()
        except mysql.connector.Error as err:
            return f"Error inserting data: {err}"

    # Step 5: Clean up
    mycursor.close()
    mydb.close()

    return "File processed and data inserted successfully!"

# Main function that takes command-line arguments
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python add_trigger.py <file_path> <user_id>")
        sys.exit(1)

    file_path = sys.argv[1]  # The path to the uploaded file
    user_id = int(sys.argv[2])  # The user ID passed from the Flask backend

    result = process_file(file_path, user_id)
    print(result)
