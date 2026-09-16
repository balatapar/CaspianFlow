$ErrorActionPreference = "Stop"

Write-Host "Running tests..." -ForegroundColor Cyan
python -m unittest discover -s tests -v

Write-Host "Building CaspianWeather for Windows..." -ForegroundColor Cyan
flet pack main.py --name CaspianWeather --product-name "هواشناس کاسپین" --file-description "Persian multi-model weather app for Nowshahr" --icon "assets\branding\caspian-weather.ico" --distpath dist --add-data "assets:assets" -y
if (!(Test-Path ".\dist\CaspianWeather.exe")) {
    throw "Flet/PyInstaller build failed: dist\CaspianWeather.exe was not created"
}

Write-Host "Build finished. Output is in .\dist" -ForegroundColor Green
Write-Host "Set GEMINI_API_KEY on the target Windows machine before using weekly analysis." -ForegroundColor Yellow
