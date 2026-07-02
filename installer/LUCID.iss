#define MyAppName "LUCID AUTO"
#define MyAppVersion "v1.0.0"
#define MyAppRelease "v1.0.0 RC14"
#define MyAppPublisher "HGPT Steel"
#define MyAppExeName "LUCID.exe"

[Setup]
AppId={{0A13B87E-05F2-4E57-9F0A-7B3E750C87D4}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\LUCID AUTO
DefaultGroupName=LUCID AUTO
DisableProgramGroupPage=yes
OutputDir=..\release\Installer
OutputBaseFilename=LUCID Setup
Compression=lzma
SolidCompression=yes
WizardStyle=modern
SetupIconFile=..\assets\LUCID.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
Source: "..\release\Windows\LUCID\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\LUCID AUTO"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\LUCID AUTO"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,LUCID AUTO}"; Flags: nowait postinstall skipifsilent
