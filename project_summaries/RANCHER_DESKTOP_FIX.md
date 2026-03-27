# Rancher Desktop Docker Access Fix

**Issue:** Docker daemon not accessible - "pipe/docker_engine: The system cannot find the file specified"

**Date:** 2026-03-27

---

## Quick Fix Options

### Option 1: Restart Rancher Desktop (Fastest)

1. **Close Rancher Desktop completely:**
   - Right-click Rancher Desktop icon in system tray
   - Click "Quit Rancher Desktop"
   - Wait 10 seconds

2. **Start Rancher Desktop as Administrator:**
   - Press Windows key
   - Type "Rancher Desktop"
   - Right-click on "Rancher Desktop"
   - Select "Run as administrator"
   - Click "Yes" when prompted

3. **Wait for it to fully start:**
   - Watch the system tray icon
   - Wait until it says "Container runtime ready" or "Running"
   - This takes 1-2 minutes

4. **Test Docker:**
   ```bash
   docker ps
   ```
   If this works, you're ready!

---

### Option 2: Switch to containerd (Alternative)

If dockerd keeps having issues:

1. Open Rancher Desktop
2. Go to Preferences/Settings
3. Under "Container Engine" select **containerd (nerdctl)**
4. Click "Apply" and wait for restart
5. Use `nerdctl` instead of `docker` commands

**Note:** This requires changing our commands, so try Option 1 first.

---

### Option 3: Use Docker Desktop Instead

If Rancher Desktop continues to have issues:

1. Uninstall Rancher Desktop
2. Download Docker Desktop: https://www.docker.com/products/docker-desktop
3. Install Docker Desktop
4. Restart computer
5. Docker Desktop usually works better on Windows

---

## What to Do Now

**Try Option 1 first:**
1. Quit Rancher Desktop (right-click tray icon → Quit)
2. Wait 10 seconds
3. Run Rancher Desktop as Administrator
4. Wait for "Running" status
5. Type "continue" in chat

**If Option 1 doesn't work after 2 tries:**
- Let me know and we'll try Option 3 (Docker Desktop)
- Docker Desktop is more stable on Windows

---

## Why This Happens

Rancher Desktop with dockerd on Windows needs:
- Administrator privileges OR
- Proper named pipe permissions OR
- WSL 2 backend properly configured

The named pipe `//./pipe/docker_engine` isn't being created, which means the Docker daemon isn't starting properly.

---

**Current Status:** Waiting for Docker daemon to be accessible
**Next Step:** Restart Rancher Desktop as Administrator
