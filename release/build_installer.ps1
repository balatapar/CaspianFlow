$ErrorActionPreference = "Stop"
$project = Split-Path $PSScriptRoot -Parent
$iscc = Get-Command iscc -ErrorAction SilentlyContinue
if (!$iscc) {
    $localIscc = Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"
    if (Test-Path $localIscc) {
        $iscc = [pscustomobject]@{ Source = $localIscc }
    }
}
if (!$iscc) {
    throw "Inno Setup is not installed. Install it from https://jrsoftware.org/isinfo.php and run this script again."
}

$exe = Join-Path $project "dist\CaspianWeather.exe"
if (!(Test-Path $exe)) {
    throw "Build the Windows executable first: .\build_windows.ps1"
}

Push-Location $PSScriptRoot
try {
    & $iscc.Source ".\build_installer.iss"
    if (!(Test-Path ".\CaspianWeather-Setup-1.0.0.exe")) {
        throw "Installer output was not created."
    }
    Write-Host "Installer created successfully." -ForegroundColor Green
} finally {
    Pop-Location
}
