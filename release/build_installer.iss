; Inno Setup script for Caspian Weather
; Install Inno Setup, then compile this file with ISCC.exe.

#define MyAppName "هواشناس کاسپین"
#define MyAppVersion "1.1.0"
#define MyAppPublisher "Caspian Weather"
#define MyAppExeName "CaspianWeather.exe"

[Setup]
AppId={{A7C2D7F1-7F8F-4D4A-9A0C-2C7D4A8F5E11}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\CaspianWeather
DefaultGroupName={#MyAppName}
OutputDir=.
OutputBaseFilename=CaspianWeather-Setup-{#MyAppVersion}
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\assets\branding\caspian-weather.ico
UninstallDisplayIcon={app}\{#MyAppExeName}
ArchitecturesInstallIn64BitMode=x64compatible
PrivilegesRequired=lowest

[Files]
Source: "..\dist\{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{autoprograms}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; WorkingDir: "{app}"; IconFilename: "{app}\{#MyAppExeName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "اجرای {#MyAppName}"; Flags: postinstall nowait skipifsilent
