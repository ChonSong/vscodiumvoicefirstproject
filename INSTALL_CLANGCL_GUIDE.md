# How to Install ClangCL for Theia

## Method 1: Using Visual Studio Installer (Recommended)

### Step 1: Open Visual Studio Installer

1. **Press Windows Key** and search for "Visual Studio Installer"
2. **Click** on "Visual Studio Installer" to open it
3. Or run this command in PowerShell:
   ```powershell
   Start-Process "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vs_installer.exe"
   ```

### Step 2: Modify Visual Studio Build Tools 2022

1. In Visual Studio Installer, find **"Visual Studio Build Tools 2022"**
2. Click the **"Modify"** button (not "Launch")

### Step 3: Select ClangCL Component

1. In the modification window, look for **"Desktop development with C++"** workload
2. **Expand** "Desktop development with C++" if it's collapsed
3. Look for **"C++ Clang Compiler for Windows"** under Individual components
4. **Check the box** next to "C++ Clang Compiler for Windows"
   - You can also search for "Clang" in the search box
   - The component ID is: `Microsoft.VisualStudio.Component.VC.Tools.ClangCL`

### Step 4: Install

1. Click the **"Modify"** button at the bottom right
2. Wait for the installation to complete (this may take 10-30 minutes)
3. You may need to restart your computer after installation

### Step 5: Verify Installation

After installation, verify ClangCL is installed:

```powershell
# Check if clang-cl.exe exists
Test-Path "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\Llvm\x64\bin\clang-cl.exe"

# Or check version
& "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\Llvm\x64\bin\clang-cl.exe" --version
```

## Method 2: Using PowerShell Script (Automated)

We have a script that attempts automated installation:

```powershell
cd d:\vscodiumvoicefirstproject
.\install-clangcl.ps1
```

**Note:** Automated installation may not always work. If it fails, use Method 1 (Visual Studio Installer GUI).

## Method 3: Using Command Line (Advanced)

If you have Visual Studio Installer in PATH, you can try:

```powershell
$vsInstallerPath = "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vs_installer.exe"
$buildToolsPath = "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
$clangClComponent = "Microsoft.VisualStudio.Component.VC.Tools.ClangCL"

Start-Process $vsInstallerPath -ArgumentList "modify --installPath `"$buildToolsPath`" --add $clangClComponent --quiet --norestart" -Verb RunAs -Wait
```

## After Installation

Once ClangCL is installed, run:

```powershell
cd d:\vscodiumvoicefirstproject\theia-fresh
.\enable-full-functionality.ps1
```

This will rebuild Theia with full native module support.

## Troubleshooting

### Issue: Visual Studio Installer not found
- **Solution:** Download and install Visual Studio Build Tools 2022 from:
  https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022

### Issue: "Desktop development with C++" not visible
- **Solution:** Make sure Visual Studio Build Tools 2022 is installed, not just Visual Studio Code

### Issue: Installation takes too long
- **Solution:** This is normal. ClangCL installation can take 10-30 minutes depending on your internet speed

### Issue: Component not found
- **Solution:** Try searching for "Clang" in the Individual components tab
- The component should be named: "C++ Clang Compiler for Windows"

## Quick Verification

After installation, check if ClangCL is working:

```powershell
# Refresh PATH
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

# Check ClangCL
clang-cl --version
```

If you see version information, ClangCL is installed correctly!



