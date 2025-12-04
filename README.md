# Customers
Sample REST API. It serves information about customers.

## Endpoints

POST parameters are sent as form-data.

|Method|Endpoint|POST params|
|------|--------|-----------|
|GET|/customers||
|GET|/customers?offset=<starting_item>||
|GET|/customers?size=<page_size>||
|GET|/customers?s=<search_term>||
|GET|/customers/<customer_id>||
|POST|/customers|first_name, last_name, phone_no (optional), address, onboarding_date|
|PUT|/customers/<customer_id>|first_name (optional), last_name (optional), phone_no (optional), address (optional), onboarding_date (optional)|
|DELETE|/customers/<customer_id>||

Default page for GET requests is 5. Search, pagination, and custom page size can be combined.

## Installation
Python 3.4 or higher required.

In the command line, run `docker-compose up -d --build`. Stop the container by running `docker-compose down`.

The endpoints will be available at `http://localhost:8001`.

## Tools
SQLite / Python / Flask

## Author
- Arturo Mora-Rioja
- HATEOAS and pagination implemented by ChatGPT 5.1, prompted by Arturo Mora-Rioja