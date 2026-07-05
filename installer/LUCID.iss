#define MyAppName "LUCID AUTO"
#ifndef MyAppVersion
  #error MyAppVersion must be supplied by the Windows release pipeline.
#endif
#ifndef MyAppRelease
  #error MyAppRelease must be supplied by the Windows release pipeline.
#endif
#define MyAppPublisher "HGPT Steel"
#define MyAppExeName "LUCID.exe"

[Setup]
AppId={{0A13B87E-05F2-4E57-9F0A-7B3E750C87D4}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppRelease}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\LUCID AUTO
DefaultGroupName=LUCID AUTO
DisableProgramGroupPage=no
UninstallDisplayIcon={app}\{#MyAppExeName}
UninstallDisplayName={#MyAppName} {#MyAppRelease}
VersionInfoVersion={#MyAppVersion}
VersionInfoCompany={#MyAppPublisher}
VersionInfoDescription={#MyAppName} Installer
VersionInfoProductName={#MyAppName}
VersionInfoProductVersion={#MyAppVersion}
VersionInfoCopyright=Copyright 2026 {#MyAppPublisher}. All rights reserved.
OutputDir=..\release\Installer
OutputBaseFilename=LUCID_Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\assets\LUCID.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: checkedonce

[Files]
Source: "..\dist\LUCID\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\LUCID AUTO"; Filename: "{app}\{#MyAppExeName}"
Name: "{group}\Uninstall LUCID AUTO"; Filename: "{uninstallexe}"
Name: "{autodesktop}\LUCID AUTO"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,LUCID AUTO}"; Flags: nowait postinstall skipifsilent
