# Docker Desktop - Next Steps

## ✅ Installation Complete!

Docker Desktop has been successfully installed via winget.

## 📋 Next Steps

### Step 1: Restart Your Computer (Usually Required)

Docker Desktop typically requires a restart to set up virtualization properly.

**Action**: Restart your computer now.

### Step 2: Launch Docker Desktop

After restart:

1. **Find Docker Desktop** in Start Menu
2. **Click to launch** "Docker Desktop"
3. **Wait for startup** (30-60 seconds)
   - Look for the whale icon in system tray
   - Wait until it shows "Docker Desktop is running"

### Step 3: Verify Installation

Open PowerShell and run:

```powershell
docker --version
docker-compose --version
```

You should see version numbers.

### Step 4: Run the Setup Script

Once Docker is running, navigate to the project directory and run:

```powershell
.\docker-setup.ps1
```

This will:
- Build the Docker containers
- Start the ADK IDE backend
- Verify everything is working

---

## 🚀 After Docker is Running

Once Docker Desktop is started, you can:

1. **Run the setup script:**
   ```powershell
   .\docker-setup.ps1
   ```

2. **Or manually start containers:**
   ```powershell
   docker-compose up --build
   ```

3. **Access the application:**
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs
   - Health Check: http://localhost:8000/health

---

## ⚠️ Troubleshooting

### "Docker is not running"
- Make sure Docker Desktop is launched
- Check system tray for whale icon
- Wait for full startup (can take up to 60 seconds)

### "WSL 2 installation is incomplete"
- Open PowerShell as Administrator
- Run: `wsl --install`
- Restart computer

### Docker commands not found
- Restart your computer (if you just installed)
- Make sure Docker Desktop is running
- Close and reopen PowerShell after Docker starts

---

## 📝 Quick Reference

**Start Docker Desktop:**
- Find in Start Menu → Launch

**Check if running:**
- Look for whale icon in system tray
- Or run: `docker info`

**Stop Docker:**
- Right-click whale icon → Quit Docker Desktop

---

**Status**: ✅ Installed - Ready to restart and launch!


