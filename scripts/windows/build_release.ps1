$ErrorActionPreference = "Stop"

Set-Location (Resolve-Path "$PSScriptRoot\..\..")

$env:PYINSTALLER_CONFIG_DIR = if ($env:PYINSTALLER_CONFIG_DIR) { $env:PYINSTALLER_CONFIG_DIR } else { (Join-Path (Get-Location) "work\pyinstaller-config") }
New-Item -ItemType Directory -Force -Path $env:PYINSTALLER_CONFIG_DIR | Out-Null

function Read-LucidVersion {
    $versionFile = "src\hgpt_ai_os\version.py"
    $content = Get-Content -Raw -Path $versionFile
    $versionMatch = [regex]::Match($content, 'APP_VERSION\s*=\s*["''](?<value>[^"'']+)["'']')
    $buildMatch = [regex]::Match($content, 'APP_BUILD\s*=\s*["''](?<value>[^"'']+)["'']')

    if (-not $versionMatch.Success) {
        throw "APP_VERSION was not found in $versionFile"
    }
    if (-not $buildMatch.Success) {
        throw "APP_BUILD was not found in $versionFile"
    }

    $appVersion = $versionMatch.Groups["value"].Value
    $appBuild = $buildMatch.Groups["value"].Value
    [pscustomobject]@{
        AppVersion = $appVersion
        Build = $appBuild
        InstallerVersion = $appVersion.TrimStart("v")
        Release = "$appVersion $appBuild"
    }
}

$version = Read-LucidVersion
$distDir = "dist\LUCID"
$installerDir = "release\Installer"
$installerName = "Lucid-AI-Studio-Setup-v$($version.InstallerVersion).exe"
$installerPath = Join-Path $installerDir $installerName
$checksumPath = "$installerPath.sha256"

python scripts\ensure_release_icons.py
python -m pip install -r requirements.txt
python -c "from PySide6.QtWidgets import QApplication; import PySide6; print('PySide6 ready:', PySide6.__file__)"
python -m PyInstaller --clean --noconfirm lucid.spec

if (-not (Test-Path -LiteralPath (Join-Path $distDir "LUCID.exe") -PathType Leaf)) {
    throw "expected PyInstaller OneDir executable was not created: dist\LUCID\LUCID.exe"
}

New-Item -ItemType Directory -Force -Path $installerDir | Out-Null
python installer\verify.py windows

$isccPath = (Get-Command ISCC.exe -ErrorAction SilentlyContinue).Source
if (-not $isccPath) {
    $candidate = "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe"
    if (Test-Path -LiteralPath $candidate -PathType Leaf) {
        $isccPath = $candidate
    }
}
if (-not $isccPath) {
    throw "ISCC.exe was not found after installing Inno Setup"
}

Remove-Item -Force -LiteralPath $installerPath, $checksumPath -ErrorAction SilentlyContinue
& $isccPath `
    "/DMyAppVersion=$($version.InstallerVersion)" `
    "/DMyAppRelease=$($version.Release)" `
    installer\LUCID.iss
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup failed with exit code $LASTEXITCODE"
}

if (-not (Test-Path -LiteralPath $installerPath -PathType Leaf)) {
    throw "expected installer was not created: $installerPath"
}

$hash = Get-FileHash -Algorithm SHA256 -LiteralPath $installerPath
"$($hash.Hash.ToLowerInvariant())  $installerName" | Set-Content -NoNewline -Encoding ascii -Path $checksumPath

if ($env:GITHUB_OUTPUT) {
    "version=$($version.InstallerVersion)" | Out-File -FilePath $env:GITHUB_OUTPUT -Append -Encoding utf8
    "installer=$installerPath" | Out-File -FilePath $env:GITHUB_OUTPUT -Append -Encoding utf8
    "checksum=$checksumPath" | Out-File -FilePath $env:GITHUB_OUTPUT -Append -Encoding utf8
}

Write-Host "Windows release ready: $installerPath"
Write-Host "Checksum ready: $checksumPath"
