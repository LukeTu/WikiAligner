; Inno Setup script for the Windows installer. Build after PyInstaller:
;   iscc /DAppVersion=0.2.0 packaging\wikialigner.iss
; Installs per user (no administrator rights), with a Start menu entry and an uninstaller.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{6E1F5D0A-3B57-4C7A-9E0B-8F1C2A7D4E31}
AppName=WikiAligner
AppVersion={#AppVersion}
AppPublisher=WikiAligner contributors
AppPublisherURL=https://github.com/LukeTu/WikiAligner
DefaultDirName={autopf}\WikiAligner
DefaultGroupName=WikiAligner
DisableProgramGroupPage=yes
DisableDirPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
OutputDir=..\dist
OutputBaseFilename=WikiAligner-Windows-x64-Setup
UninstallDisplayIcon={app}\WikiAligner.exe
Compression=lzma2/fast
SolidCompression=no
WizardStyle=modern
LicenseFile=..\LICENSE

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\dist\WikiAligner\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{autoprograms}\WikiAligner"; Filename: "{app}\WikiAligner.exe"
Name: "{autodesktop}\WikiAligner"; Filename: "{app}\WikiAligner.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\WikiAligner.exe"; Description: "{cm:LaunchProgram,WikiAligner}"; Flags: nowait postinstall skipifsilent
