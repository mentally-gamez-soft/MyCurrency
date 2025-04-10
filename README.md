# MyCurrency
POC for API currency exchange with DRF

This is a Django Rest project and as such a set of command reminders are prompted in this document.

## 1. Create the python venv and install the dependencies:
    pip install pip-tools
    pip-compile requirements.in
    pip install -r requirements.txt

## 2. copy the .env.keys in /MYCURRENCY directory

## 3. Execute the DB migrations:
    python ./manage.py migrate

## 4. Create the super user and the manager user and his group and permissions:
    python ./manage.py create_groups_and_users

## 5. Create the providers (2 for currency beacon and 2 mocks):
    python ./manage.py create_providers

## 6. Create the currencies:
    python ./manage.py create_currencies

## 7. Add the exchange rate data history:
    python ./manage.py bulk_import_exchange_rates_dataset

## 8. Starting the redis cache server
    cd ./build-run-commands
    ./002.a.start-redis-cache.ps1

## 9. execute the application
    python ./manage.py runserver 8003 

## 10. go to endpoints
    http://localhost:8003/api/v1/currency
    http://localhost:8003/api/v1/currency-converter/?from_currency=GBP&to_currency=CHF&valuation_date=2025-4-1

## Starting the database container
    # cd ./build-run-commands
    # ./001.a.start-database.ps1

## Execution of coverage
coverage run --source="." manage.py test


