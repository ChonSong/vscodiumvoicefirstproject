# Script to add ClangCL to Visual Studio Build Tools 2022
# Run this script as Administrator

$installerPath = "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vs_installer.exe"
$buildToolsPath = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"

if (-not (Test-Path $installerPath)) {
    Write-Host "Visual Studio Installer not found at: $installerPath"
    Write-Host "Please install Visual Studio Build Tools first."
    exit 1
}

Write-Host "Adding ClangCL component to Visual Studio Build Tools 2022..."
Write-Host "This may take several minutes..."

# Add ClangCL component
$arguments = @(
    "modify",
    "--installPath", "`"$buildToolsPath`"",
    "--add", "Microsoft.VisualStudio.Component.VC.Tools.ClangCL",
    "--add", "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
    "--quiet",
    "--norestart"
)

Start-Process -FilePath $installerPath -ArgumentList $arguments -Wait -NoNewWindow

Write-Host ""
Write-Host "Installation complete! Please verify by running:"
Write-Host "clang-cl --version"
Write-Host ""
Write-Host "If clang-cl is not found, you may need to:"
Write-Host "1. Open Visual Studio Installer manually"
Write-Host "2. Modify Visual Studio Build Tools 2022"
Write-Host "3. Under 'Desktop development with C++', check 'C++ Clang Compiler for Windows'"
Write-Host "4. Click Modify to install"



