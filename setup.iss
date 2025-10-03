; setup.iss
[Setup]
AppName=ToriiKanji
AppVersion=1.0
DefaultDirName={autopf64}\ToriiKanji
DefaultGroupName=ToriiKanji
UninstallDisplayIcon={app}\ToriiKanji.exe
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
OutputBaseFilename=ToriiKanji-Setup-v1.0
SetupIconFile=assets\Icon\Icon.ico
UninstallIconFile=assets\Icon\Icon.ico

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "brazilianportuguese"; MessagesFile: "compiler:Languages\BrazilianPortuguese.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\ToriiKanji\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\ToriiKanji"; Filename: "{app}\ToriiKanji.exe"
Name: "{autodesktop}\ToriiKanji"; Filename: "{app}\ToriiKanji.exe"; Tasks: desktopicon