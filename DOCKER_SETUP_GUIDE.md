# Docker Setup Guide for ADK IDE

## Docker Installation

### Step 1: Install Docker Desktop

**Windows:**
1. Download Docker Desktop for Windows from: https://www.docker.com/products/docker-desktop/
2. Run the installer (`Docker Desktop Installer.exe`)
3. Follow the installation wizard
4. Restart your computer when prompted
5. Launch Docker Desktop from Start Menu
6. Wait for Docker to start (whale icon in system tray)

### Step 2: Verify Installation

Open PowerShell and run:
```powershell
docker --version
docker-compose --version
```

You should see version numbers for both commands.

### Step 3: Configure Docker Desktop

1. Open Docker Desktop
2. Go to Settings → General
3. Ensure "Use WSL 2 based engine" is checked (if available)
4. Apply & Restart if needed

---

## Running ADK IDE with Docker

### Quick Start

Once Docker is installed, run:

```powershell
# Build and start the container
docker-compose up --build

# Or run in detached mode (background)
docker-compose up -d --build
```

### Access the Application

- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Metrics**: http://localhost:8000/metrics

### View Logs

```powershell
# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f adk-ide
```

### Stop the Container

```powershell
# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Environment Variables

The Docker setup uses the `.env` file in the project root. Make sure it contains:

```
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
GOOGLE_API_KEY=your-api-key
ENVIRONMENT=development
```

**Note**: If using Docker, you may need to adjust `GOOGLE_APPLICATION_CREDENTIALS` to a path inside the container or use a volume mount.

---

## Troubleshooting

### Docker not starting
- Ensure virtualization is enabled in BIOS
- Check Windows features: Virtual Machine Platform, Windows Subsystem for Linux

### Port already in use
- Change port in `docker-compose.yml`: `"8080:8000"` instead of `"8000:8000"`

### Build fails
- Check Docker Desktop is running
- Ensure `.env` file exists
- Review error messages in `docker-compose logs`

### Container exits immediately
```powershell
# Check logs
docker-compose logs adk-ide

# Run interactively to debug
docker-compose run --rm adk-ide /bin/bash
```

---

## Alternative: Local Python Setup

If Docker installation is problematic, you can use local Python setup instead:

1. Install Python 3.8+ from https://www.python.org/downloads/
2. Create virtual environment: `python -m venv .venv`
3. Activate: `.venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run: `uvicorn main:app --reload`

See `ACTION_PLAN.md` for detailed local setup instructions.


