# Stock Alert Application

A full-stack application for tracking stock prices and setting up price deviation alerts based on NSE (National Stock Exchange) data.

## Overview

The Stock Alert Application allows users to:
- Set up triggers for stock price movements
- Upload and manage HNI (High Net worth Individual) details
- View active and inactive triggers
- Receive alerts when stocks cross specified price thresholds
- Upload data in bulk via CSV files

## Technology Stack

### Backend
- Python Flask API
- MySQL Database
- Scheduled tasks for data retrieval and comparison

### Frontend
- React.js
- React Router for navigation
- Axios for API communication

## Prerequisites

- Python 3.7+
- Node.js 16+ and npm
- MySQL Database Server
- Git (optional, for cloning)

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd stock-alert-application
```

### 2. Database Setup
1. Create a MySQL database named `stocks_view`
2. Import the schema using the provided SQL file:
```bash
mysql -u username -p stocks_view < stocks_view.sql
```

### 3. Configure Database Connection
Edit the `_config.py` file with your database credentials:
```python
DB_HOST = "your_host" # usually "localhost" or "127.0.0.1"
DB_PORT = 3306
DB_NAME = "stocks_view"
DB_USER = "your_username"
DB_PASSWORD = "your_password"
```

### 4. Install Backend Dependencies
```bash
pip install flask flask-cors mysql-connector-python pandas requests schedule
```

### 5. Install Frontend Dependencies
```bash
npm install
```

## Running the Application

### Starting the Backend
```bash
python server.py
```
Or use the provided start script:
```bash
chmod +x start.sh
./start.sh
```

### Starting the Frontend (Development Mode)
```bash
npm start
```

### Building for Production
```bash
npm run build
```

## Key Features

### 1. User Authentication
- Secure login system
- Session management

### 2. Trigger Management
- Create, edit, and delete price movement triggers
- Set price deviation thresholds for alerts
- Mark triggers as active or inactive

### 3. HNI Details
- Upload and manage HNI information
- Link HNI details to specific stocks

### 4. Data Import/Export
- Upload trigger data in bulk via CSV
- Upload HNI data in bulk via CSV

### 5. Automated Data Processing
- Daily fetching of NSE bhavcopy data
- Automated comparison of market prices against triggers
- Alert generation

## Application Structure

### Backend Components
- `server.py`: Main Flask application with API endpoints
- `bhavcopydata.py`: Script to fetch and process NSE bhavcopy data
- `compare.py`: Script to compare stock prices with triggers
- `onDemand.py`: On-demand data processing
- `hni_input.py`: HNI data processing
- `add_trigger.py`: Trigger management

### Frontend Components
- React components in `src/components/`
- Page views in `src/pages/`
- Main application in `src/App.js`

## API Endpoints

### Authentication
- `/login` (POST): User login

### Triggers
- `/active-triggers/<user_id>` (GET): Fetch active triggers
- `/inactive-triggers/<user_id>` (GET): Fetch inactive triggers
- `/all-triggers/<user_id>` (GET): Fetch all triggers
- `/active-triggers/<user_id>` (POST): Add new trigger
- `/active-triggers/<user_id>/<trigger_id>` (PUT): Update trigger
- `/active-triggers/<user_id>/<trigger_id>` (DELETE): Delete trigger

### HNI Details
- `/hni-details` (GET): Fetch all HNI details
- `/hni-details` (POST): Add new HNI detail
- `/hni-details/<symbol>` (PUT): Update HNI detail
- `/hni-details/<symbol>` (DELETE): Delete HNI detail

### File Upload
- `/upload-hni-file` (POST): Upload HNI details file
- `/upload-triggers-file/<user_id>` (POST): Upload triggers file

## Automated Tasks
The system runs scheduled tasks:
- 8:00 AM and 6:00 PM daily: Fetch NSE bhavcopy data
- 8:00 AM and 6:00 PM daily: Compare prices against triggers

## Troubleshooting

### Logs
- Check logs in the `logs/` directory for issues
- Each log file is timestamped with the format `app_YYYYMMDD_HHMMSS.log`

### Common Issues
- Database connection issues: Verify credentials in `_config.py`
- Data fetch issues: Check internet connectivity and NSE website status
- Permission issues: Ensure the application has necessary file system permissions

## License

[Specify your license here]
