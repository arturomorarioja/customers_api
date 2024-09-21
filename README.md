# Customers
Sample REST API. It serves information about customers.

## Endpoints

POST parameters are sent as form-data.

|Method|Endpoint|POST params|
|------|--------|-----------|
|GET|/customers||
|GET|/customers?s=<search_term>||
|GET|/customers/<customer_id>||
|POST|/customers|first_name, last_name, phone_no (optional), address, onboarding_date|
|PUT|/customers/<customer_id>|first_name (optional), last_name (optional), phone_no (optional), address (optional), onboarding_date (optional)|
|DELETE|/customers/<customer_id>||

## Installation
Python 3.4 or higher required.

1. Create a virtual environment:
```
python -m venv venv
```

2. Activate the virtual environment.
Windows cmd: `.\venv\Scripts\activate`.
Windows Powershell: `.\venv\Scripts\Activate.psl`.
Linux and Mac: `source venv/bin/activate`.

3. Install dependencies:
```
pip install Flask
pip install python-dotenv
```

4. Create and populate the database:
```
python -m flask --app customers init-db
```

## Running the API
Within (venv), run:
```
python -m flask --app customers run --port 8001 --debug
```
The endpoints will be available at `http://localhost:8001`.

## Tools
SQLite / Python / Flask

## Author
Arturo Mora-Rioja