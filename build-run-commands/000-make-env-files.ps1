



Write-Host "* Copying .env file to dotenv-file-maker directory.";
Get-Item -Path ..\.env | Copy-Item -Destination .\dotenv-file-maker\.env;

cd .\dotenv-file-maker;
Write-Host "* Changed to directory dotenv-file-maker:";
Get-Location;

Write-Host "* Creating and encrypting .env.vault and .env.keys files.";
npx dotenv-vault local build

Write-Host "* Delete .gitignore file";
Remove-Item -Path .\.gitignore;

# Write-Host "* Delete .env file";
# Remove-Item -Path .\.env;

Write-Host "* Moving .env.vault file to root project directory.";
Get-Item -Path .\.env.vault | Move-Item -Destination ..\..\.env.vault;

Write-Host "* Moving .env.keys file root project directory";
Get-Item -Path .\.env.keys | Move-Item -Destination ..\..\.env.keys;