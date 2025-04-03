from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS  # Import the CORS library
import mysql.connector
from mysql.connector import pooling
import schedule
import time
import subprocess
import threading
import sys
from datetime import datetime
import os
import tempfile
import shutil
from werkzeug.utils import secure_filename
from _config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER

# Get current date and time
current_time = datetime.now().strftime('%Y%m%d_%H%M%S')

# Create a unique log file name with a timestamp
log_filename = f'app_{current_time}.log'

# Create logs directory if it doesn't exist 
os.makedirs('logs', exist_ok=True)

# Full path for the log file 
log_filepath = os.path.join('logs', log_filename)
 
# Open the log file in append mode 
log_file = open(log_filepath, 'a')
 
# Redirect stdout and stderr to the log file 
sys.stdout = log_file 
sys.stderr = log_file

# Database configuration
db_config = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME
}

# Create a connection pool
pool = pooling.MySQLConnectionPool(
    pool_name="stocks_pool",
    pool_size=10,
    **db_config
)

# Define the functions to run the scripts
def run_bhavcopydata():
    print("Running bhavcopydata.py...")
    subprocess.run(['python', 'bhavcopydata.py'])

def run_compare():
    print("Running compare.py...")
    subprocess.run(['python', 'compare.py'])

# Schedule the tasks
schedule.every().day.at("08:00").do(run_bhavcopydata)
schedule.every().day.at("08:00").do(run_compare)
schedule.every().day.at("18:00").do(run_bhavcopydata)
schedule.every().day.at("18:00").do(run_compare)

# Function to run scheduled tasks in a separate thread
def run_scheduled_tasks():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduled tasks in a separate thread
threading.Thread(target=run_scheduled_tasks, daemon=True).start()

# Initialize Flask app
app = Flask(__name__, static_folder='stocks-view-ui/build')
CORS(app)  # Enable CORS for all routes

@app.route('/') 
def serve(): 
    return send_from_directory(app.static_folder, 'index.html') 

@app.route('/<path:path>') 
def static_proxy(path): 
    return send_from_directory(app.static_folder, path) 

def get_db_connection():
    """Retrieve a connection from the connection pool"""
    return pool.get_connection()

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    try:
        connection = get_db_connection()  # Fetch connection from the pool
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE USERNAME = %s AND PASSWORD = %s", (username, password))
        user = cursor.fetchone()
        connection.close()  # Return connection to the pool

        if user:
            return jsonify({"success": True, "user_id": user["USER_ID"]})
        else:
            return jsonify({"success": False, "message": "Invalid credentials"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/active-triggers/symbols', methods=['GET'])
def get_symbols():
    try:
        connection = get_db_connection()  # Fetch connection from the pool
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT SYMBOL FROM bhavcopydata")
        symbols = cursor.fetchall()
        connection.close()  # Return connection to the pool

        return jsonify([symbol['SYMBOL'] for symbol in symbols]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/active-triggers/series', methods=['GET'])
def get_series():
    try:
        connection = get_db_connection()  # Fetch connection from the pool
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT DISTINCT SERIES FROM bhavcopydata")
        series = cursor.fetchall()
        connection.close()  # Return connection to the pool

        return jsonify([s['SERIES'] for s in series]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/all-triggers/<user_id>', methods=['GET'])
def get_all_triggers(user_id):
    try:
        connection = get_db_connection()  # Fetch connection from the pool
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM active_triggers WHERE USER_ID = %s", (user_id,))
        triggers = cursor.fetchall()
        connection.close()  # Return connection to the pool
        return jsonify(triggers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/active-triggers/<user_id>', methods=['GET'])
def get_active_triggers(user_id):
    try:
        connection = get_db_connection()  # Fetch connection from the pool
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM active_triggers WHERE USER_ID = %s AND STATUS = %s", (user_id,'ACTIVE'))
        triggers = cursor.fetchall()
        connection.close()  # Return connection to the pool

        return jsonify(triggers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/inactive-triggers/<user_id>', methods=['GET'])
def get_inactive_triggers(user_id):
    try:
        connection = get_db_connection()  # Fetch connection from the pool
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM active_triggers WHERE USER_ID = %s AND STATUS = %s", (user_id, 'INACTIVE'))
        triggers = cursor.fetchall()
        connection.close()  # Return connection to the pool

        return jsonify(triggers), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/active-triggers/<user_id>', methods=['POST'])
def add_trigger(user_id):
    try:
        data = request.json
        trigger_id = data['trigger_id']  # Use trigger_id generated by the frontend
        symbol = data['symbol']
        series = data['series']
        lop = data.get('lop')
        bop = data.get('bop')
        deviation = data['deviation']
        comments = data.get('comments', '')
        status = data['status']

        connection = get_db_connection()  # Fetch connection from the pool
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            INSERT INTO active_triggers (USER_ID, TRIGGER_ID, SYMBOL, SERIES, LOP, BOP, DEVIATION, COMMENTS, STATUS)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (user_id, trigger_id, symbol, series, lop, bop, deviation, comments, status))
        connection.commit()
        connection.close()

        # Update the active_triggers HNI after uploading HNI file
        update_active_triggers_hni()

        return jsonify({
            "message": "Trigger added successfully",
            "USER_ID": user_id,
            "TRIGGER_ID": trigger_id,
            "SYMBOL": symbol,
            "SERIES": series,
            "LOP": lop,
            "BOP": bop,
            "DEVIATION": deviation,
            "COMMENTS": comments,
            "STATUS": status
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/active-triggers/<user_id>/<trigger_id>', methods=['DELETE'])
def delete_trigger(user_id, trigger_id):
    try:
        connection = get_db_connection()  # Fetch connection from the pool
        cursor = connection.cursor()
        cursor.execute("DELETE FROM active_triggers WHERE USER_ID = %s AND TRIGGER_ID = %s", (user_id, trigger_id))
        connection.commit()
        connection.close()  # Return connection to the pool

        return jsonify({"message": "Trigger deleted successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/active-triggers/<user_id>/<trigger_id>', methods=['PUT'])
def edit_trigger(user_id, trigger_id):
    data = request.json

    # Validate required fields
    symbol = data.get('SYMBOL')
    series = data.get('SERIES')
    deviation = data.get('DEVIATION')
    status = data.get('STATUS')

    # Optional fields with defaults
    lop = data.get('LOP')
    bop = data.get('BOP')
    comments = data.get('COMMENTS', '')

    try:
        connection = get_db_connection()  # Fetch connection from the pool
        cursor = connection.cursor(dictionary=True)
        cursor.execute("""
            UPDATE active_triggers
            SET SYMBOL = %s, SERIES = %s, LOP = %s, BOP = %s, DEVIATION = %s, COMMENTS = %s, STATUS = %s
            WHERE USER_ID = %s AND TRIGGER_ID = %s
        """, (symbol, series, lop, bop, deviation, comments, status, user_id, trigger_id))
        connection.commit()
        connection.close()  # Return connection to the pool

        if cursor.rowcount == 0:  # No rows were updated
            return jsonify({"error": "Trigger not found or no changes made"}), 404

        return jsonify({
            "message": "Trigger updated successfully",
            "USER_ID": user_id,
            "TRIGGER_ID": trigger_id,
            "SYMBOL": symbol,
            "SERIES": series,
            "LOP": lop,
            "BOP": bop,
            "DEVIATION": deviation,
            "COMMENTS": comments,
            "STATUS": status
        }), 200

    except Exception as e:
        return jsonify({"error": "Failed to update trigger", "details": str(e)}), 500

@app.route('/previous-triggers/<user_id>', methods=['GET'])
def get_previous_triggers(user_id):
    try:
        connection = get_db_connection()  # Fetch connection from the pool
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM alerts_table WHERE USER_ID = %s", (user_id,))
        triggers = cursor.fetchall()
        connection.close()  # Return connection to the pool

        return jsonify(triggers)
    
    except Exception as e:
        return jsonify({"error": str(e), "message": "Failed to fetch previous triggers"}), 500
    
@app.route('/custom-triggers/<user_id>', methods=['GET'])
def get_custom_triggers(user_id):
    try:
        connection = get_db_connection()  # Fetch connection from the pool
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM custom_triggers WHERE USER_ID = %s", (user_id,))
        triggers = cursor.fetchall()
        connection.close()  # Return connection to the pool

        return jsonify(triggers)
    
    except Exception as e:
        return jsonify({"error": str(e), "message": "Failed to fetch custom triggers"}), 500

@app.route('/api/submit-date', methods=['POST'])
def submit_date():
    # Get the JSON data from the request
    data = request.get_json()
    
    # Extract the 'date' and 'user_id' values from the request
    user_date = data.get('date')
    user_id = data.get('user_id')
    print(user_date)
    # Check if both 'date' and 'user_id' are provided
    if not user_date or not user_id:
        return jsonify({'status': 'error', 'message': 'Missing date or user_id'}), 400

    try:
        # Call the onDemand.py script using subprocess and pass both date and user_id as arguments
        print(f"Running onDemand.py with user_id: {user_id} and date: {user_date}")
        result = subprocess.check_output(['python', 'onDemand.py', log_filepath, user_id, user_date], text=True)
        
        # Return the output from the onDemand.py script
        return jsonify({
            'status': 'success',
            'received_date': user_date,
            'received_user_id': user_id,
            'result': result
        })

    except subprocess.CalledProcessError as e:
        # Handle error in case the subprocess call fails
        print(f"Error running onDemand.py: {e}")
        return jsonify({'status': 'error', 'message': 'Error running onDemand.py'}), 500

    
    except subprocess.CalledProcessError as e:
        # Handle errors in the subprocess execution
        return jsonify({'status': 'error', 'message': e.output})

@app.route('/hni-details', methods=['GET'])
def get_hni_details():
    """
    Endpoint to fetch all HNI details from the `hni_list` table.
    """
    try:
        connection = get_db_connection()  # Fetch connection from the pool
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT SYMBOL, COMPANY_NAME, HNI_DETAILS FROM hni_list")
        hni_details = cursor.fetchall()
        connection.close()  # Return connection to the pool

        # Return the fetched data as JSON
        return jsonify(hni_details), 200

    except Exception as e:
        # Handle errors and return appropriate response
        return jsonify({"error": str(e), "message": "Failed to fetch HNI details"}), 500

@app.route('/hni-details', methods=['POST'])
def add_hni_detail():
    data = request.json
    symbol = data.get('SYMBOL')
    company_name = data.get('COMPANY_NAME')
    hni_details = data.get('HNI_DETAILS')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO hni_list (SYMBOL, COMPANY_NAME, HNI_DETAILS)
            VALUES (%s, %s, %s)
        """, (symbol, company_name, hni_details))
        connection.commit()
        connection.close()

        # Update the active_triggers HNI after uploading HNI file
        update_active_triggers_hni()

        return jsonify({"message": "HNI detail added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/hni-details/<symbol>', methods=['PUT'])
def edit_hni_detail(symbol):
    data = request.json
    company_name = data.get('COMPANY_NAME')
    new_hni_details = data.get('HNI_DETAILS')
    current_hni_details = data.get('CURRENT_HNI_DETAILS')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE hni_list
            SET COMPANY_NAME = %s, HNI_DETAILS = %s
            WHERE SYMBOL = %s AND HNI_DETAILS = %s
        """, (company_name, new_hni_details, symbol, current_hni_details))
        connection.commit()
        connection.close()

        return jsonify({"message": "HNI detail updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/hni-details/<symbol>', methods=['DELETE'])
def delete_hni_detail(symbol):
    data = request.json
    hni_details = data.get('HNI_DETAILS')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM hni_list
            WHERE SYMBOL = %s AND HNI_DETAILS = %s
        """, (symbol, hni_details))
        connection.commit()
        connection.close()

        return jsonify({"message": "HNI detail deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def update_active_triggers_hni():
    try:
        # Get a connection from the pool
        connection = get_db_connection()
        cursor = connection.cursor()

        # Define the SQL query
        q2 = """
        UPDATE active_triggers AT
        JOIN (
            SELECT SYMBOL, GROUP_CONCAT(HNI_DETAILS ORDER BY HNI_DETAILS ASC) AS concatenated_hnis
            FROM hni_list
            GROUP BY SYMBOL
        ) HL
        ON AT.SYMBOL = HL.SYMBOL
        SET AT.HNI = HL.concatenated_hnis;
        """

        # Execute the query
        cursor.execute(q2)
        connection.commit()

        print(f"{cursor.rowcount} rows updated in active_triggers.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        # Ensure connection and cursor are closed properly
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Update Flask route for uploading the Excel file
@app.route('/upload-hni-file', methods=['POST'])
def upload_hni_file():
    try:
        # Check if the file is part of the request
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        # Ensure a file is selected
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Save the file temporarily
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)

        # Call the hni_input.py script with the file path
        result = subprocess.check_output(['python', 'hni_input.py', file_path], text=True)

        # Clean up by removing the temporary directory and file
        shutil.rmtree(temp_dir)

        # Update the active_triggers HNI after uploading HNI file
        update_active_triggers_hni()

        return jsonify({"status": "success", "message": result.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload-triggers-file/<user_id>', methods=['POST'])
def upload_triggers_file(user_id):
    try:
        # Check if the file is part of the request
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        # Ensure a file is selected
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Save the file temporarily
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)

        # Call the add_trigger.py script with both the file path and user_id
        result = subprocess.check_output(
            ['python', 'add_trigger.py', file_path, user_id], text=True
        )

        # Clean up by removing the temporary directory and file
        shutil.rmtree(temp_dir)

        # Update the active_triggers HNI after uploading HNI file
        update_active_triggers_hni()

        # Return the success message from the script output
        return jsonify({"status": "success", "message": result.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run', methods=['GET'])
def runCompare():
    try:
        print("Running compare.py...")
        subprocess.run(['python', 'compare.py'])

        return jsonify({"message": "Trigger run successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/hni-details', methods=['GET'])
def get_hni_details():
    """
    Endpoint to fetch all HNI details from the `hni_list` table.
    """
    try:
        connection = get_db_connection()  # Fetch connection from the pool
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT SYMBOL, COMPANY_NAME, HNI_DETAILS FROM hni_list")
        hni_details = cursor.fetchall()
        connection.close()  # Return connection to the pool

        # Return the fetched data as JSON
        return jsonify(hni_details), 200

    except Exception as e:
        # Handle errors and return appropriate response
        return jsonify({"error": str(e), "message": "Failed to fetch HNI details"}), 500

@app.route('/hni-details', methods=['POST'])
def add_hni_detail():
    data = request.json
    symbol = data.get('SYMBOL')
    company_name = data.get('COMPANY_NAME')
    hni_details = data.get('HNI_DETAILS')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO hni_list (SYMBOL, COMPANY_NAME, HNI_DETAILS)
            VALUES (%s, %s, %s)
        """, (symbol, company_name, hni_details))
        connection.commit()
        connection.close()

        # Update the active_triggers HNI after uploading HNI file
        update_active_triggers_hni()

        return jsonify({"message": "HNI detail added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/hni-details/<symbol>', methods=['PUT'])
def edit_hni_detail(symbol):
    data = request.json
    company_name = data.get('COMPANY_NAME')
    new_hni_details = data.get('HNI_DETAILS')
    current_hni_details = data.get('CURRENT_HNI_DETAILS')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            UPDATE hni_list
            SET COMPANY_NAME = %s, HNI_DETAILS = %s
            WHERE SYMBOL = %s AND HNI_DETAILS = %s
        """, (company_name, new_hni_details, symbol, current_hni_details))
        connection.commit()
        connection.close()

        return jsonify({"message": "HNI detail updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/hni-details/<symbol>', methods=['DELETE'])
def delete_hni_detail(symbol):
    data = request.json
    hni_details = data.get('HNI_DETAILS')

    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            DELETE FROM hni_list
            WHERE SYMBOL = %s AND HNI_DETAILS = %s
        """, (symbol, hni_details))
        connection.commit()
        connection.close()

        return jsonify({"message": "HNI detail deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def update_active_triggers_hni():
    try:
        # Get a connection from the pool
        connection = get_db_connection()
        cursor = connection.cursor()

        # Define the SQL query
        q2 = """
        UPDATE active_triggers AT
        JOIN (
            SELECT SYMBOL, GROUP_CONCAT(HNI_DETAILS ORDER BY HNI_DETAILS ASC) AS concatenated_hnis
            FROM hni_list
            GROUP BY SYMBOL
        ) HL
        ON AT.SYMBOL = HL.SYMBOL
        SET AT.HNI = HL.concatenated_hnis;
        """

        # Execute the query
        cursor.execute(q2)
        connection.commit()

        print(f"{cursor.rowcount} rows updated in active_triggers.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        # Ensure connection and cursor are closed properly
        if cursor:
            cursor.close()
        if connection:
            connection.close()

# Allowed file extensions
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Update Flask route for uploading the Excel file
@app.route('/upload-hni-file', methods=['POST'])
def upload_hni_file():
    try:
        # Check if the file is part of the request
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        # Ensure a file is selected
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Save the file temporarily
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)

        # Call the hni_input.py script with the file path
        result = subprocess.check_output(['python', 'hni_input.py', file_path], text=True)

        # Clean up by removing the temporary directory and file
        shutil.rmtree(temp_dir)

        # Update the active_triggers HNI after uploading HNI file
        update_active_triggers_hni()

        return jsonify({"status": "success", "message": result.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload-triggers-file/<user_id>', methods=['POST'])
def upload_triggers_file(user_id):
    try:
        # Check if the file is part of the request
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        
        file = request.files['file']
        
        # Ensure a file is selected
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        # Save the file temporarily
        temp_dir = tempfile.mkdtemp()
        file_path = os.path.join(temp_dir, file.filename)
        file.save(file_path)

        # Call the add_trigger.py script with both the file path and user_id
        result = subprocess.check_output(
            ['python', 'add_trigger.py', file_path, user_id], text=True
        )

        # Clean up by removing the temporary directory and file
        shutil.rmtree(temp_dir)

        # Update the active_triggers HNI after uploading HNI file
        update_active_triggers_hni()

        # Return the success message from the script output
        return jsonify({"status": "success", "message": result.strip()})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/run', methods=['GET'])
def runCompare():
    try:
        print("Running compare.py...")
        subprocess.run(['python', 'compare.py'])

        return jsonify({"message": "Trigger run successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

# Close the log file when done 
log_file.close()