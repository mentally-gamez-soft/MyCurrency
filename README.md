# MyCurrency
POC for API currency exchange

## creation of the couple of files .env.keys/.env.vault from a .env file - needs npx installed
The program will use the .env.vault available in the source code. But the key needs to be created.

    > cd build-run-commands
    > ./000-make-env-files.ps1

## Starting the database container
    # cd ./build-run-commands
    # ./001.a.start-database.ps1
