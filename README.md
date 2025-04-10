# MyCurrency
POC for API currency exchange with DRF

This is a Django Rest project and as such a set of command reminders are prompted in this document.

## 1. Execute the DB migrations:
    python ./manage.py migrate

## 2. Create the super user and the manager user and his group and permissions:
    python ./manage.py create_groups_and_users

## 3. Create the providers (2 for currency beacon and 2 mocks):
    python ./manage.py create_providers

## 4. Create the currencies:
    python ./manage.py create_currencies

## 5. Add the exchange rate data history:
    python ./manage.py bulk_import_exchange_rates_dataset

## Starting the database container
    # cd ./build-run-commands
    # ./001.a.start-database.ps1

## Execution of coverage
coverage run --source="." manage.py test


