# Docker Installation Instructions

## Quick Install

### For Windows:

1. **Download Docker Desktop**
   - Go to: https://www.docker.com/products/docker-desktop/
   - Click "Download for Windows"
   - Save the installer file

2. **Run the Installer**
   - Double-click `Docker Desktop Installer.exe`
   - Follow the installation wizard
   - Accept the license agreement
   - Choose installation location (default is fine)
   - **Important**: Check "Use WSL 2 instead of Hyper-V" if prompted
   - Click "Install"

3. **Restart Your Computer**
   - Docker will prompt you to restart
   - Restart when installation completes

4. **Launch Docker Desktop**
   - Find "Docker Desktop" in Start Menu
   - Click to launch
   - Wait for Docker to start (whale icon appears in system tray)
   - You may need to accept the terms of service

5. **Verify Installation**
   - Open PowerShell
   - Run: `docker --version`
   - You should see: `Docker version XX.XX.XX, build ...`

## System Requirements

- **Windows 10 64-bit**: Pro, Enterprise, or Education (Build 19041 or higher)
- **OR Windows 11 64-bit**: Home or Pro version 21H2 or higher
- **WSL 2 feature enabled**
- **Virtualization enabled in BIOS**

### Enable WSL 2 (if needed)

1. Open PowerShell as Administrator
2. Run:
   ```powershell
   wsl --install
   ```
3. Restart your computer
4. After restart, WSL 2 will be configured

### Enable Virtualization (if needed)

1. Restart your computer
2. Enter BIOS/UEFI settings (usually F2, F10, or Del during boot)
3. Find "Virtualization" or "VT-x" or "AMD-V"
4. Enable it
5. Save and exit

## After Installation

Once Docker is installed and running:

1. **Run the setup script:**
   ```powershell
   .\docker-setup.ps1
   ```

2. **Or manually start:**
   ```powershell
   docker-compose up --build
   ```

## Troubleshooting

### "Docker is not running"
- Make sure Docker Desktop is launched
- Check system tray for Docker icon
- Wait for Docker to fully start (can take 30-60 seconds)

### "WSL 2 installation is incomplete"
- Run: `wsl --install` in PowerShell as Administrator
- Restart computer

### "Virtualization is not enabled"
- Enable virtualization in BIOS (see above)
- Restart computer

### Installation takes too long
- This is normal, Docker Desktop is a large application
- Initial download is ~500MB
- Installation can take 5-10 minutes

## Alternative: Use Local Python

If Docker installation is problematic, you can use local Python instead:

1. Install Python 3.8+ from https://www.python.org/downloads/
2. Create virtual environment: `python -m venv .venv`
3. Activate: `.venv\Scripts\activate`
4. Install: `pip install -r requirements.txt`
5. Run: `uvicorn main:app --reload`

See `ACTION_PLAN.md` for details.


