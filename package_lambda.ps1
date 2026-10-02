# package_lambda.ps1
Write-Host "Cleaning up previous builds..."
if (Test-Path "package") { Remove-Item -Recurse -Force package }
if (Test-Path "backend.zip") { Remove-Item -Force backend.zip }

Write-Host "Installing backend dependencies..."
pip install --target ./package -r requirements.txt

Write-Host "Copying backend code..."
Copy-Item -Path "backend" -Destination "package/backend" -Recurse

Write-Host "Zipping package..."
Compress-Archive -Path "package\*" -DestinationPath "backend.zip"

Write-Host "Cleanup temporary package folder..."
Remove-Item -Recurse -Force package

Write-Host "Done! backend.zip is ready for AWS Lambda upload."
