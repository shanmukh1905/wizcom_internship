import sys
import pandas as pd
import mysql.connector
from _config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

# Check if the file path is provided
if len(sys.argv) < 2:
    print("Error: Excel file path not provided.")
    sys.exit(1)

# Get the file path from command line arguments
excel_file = sys.argv[1]

# Connect to the database
mydb = mysql.connector.connect(
    host= DB_HOST,
    user= DB_USER,
    password= DB_PASSWORD,
    database= DB_NAME
)

mycursor = mydb.cursor()

# Read the Excel file
df = pd.read_excel(excel_file)

# Insert data into MySQL table
for index, row in df.iterrows():
    symbol = row['SYMBOL']
    company_name = row['COMPANY_NAME']
    hni_details = row['HNI_DETAILS']
    
    insert_query = """
    INSERT IGNORE INTO hni_list (SYMBOL, COMPANY_NAME, HNI_DETAILS)
    VALUES (%s, %s, %s)
    """
    mycursor.execute(insert_query, (symbol, company_name, hni_details))

# Commit changes and close the connection
mydb.commit()
mycursor.close()
mydb.close()

print("Data has been inserted successfully.")
