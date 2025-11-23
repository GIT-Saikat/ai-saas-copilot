# How to Start Frontend and Backend Servers

## Quick Start (Both Servers)

### Option 1: Separate Terminals (Recommended)

**Terminal 1 - Backend:**
```bash
cd backend
python run_server.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm start
```

### Option 2: Using PowerShell (Windows)

**Backend:**
```powershell
cd backend; python run_server.py
```

**Frontend (in new PowerShell window):**
```powershell
cd frontend; npm start
```

## Verification

### 1. Check Backend is Running
- Open: http://localhost:8000/api/health
- Should return: `{"status":"healthy","version":"1.0.0"}`
- API Docs: http://localhost:8000/docs

### 2. Check Frontend is Running
- Open: http://localhost:3000
- Should see the Support Copilot interface
- Connection status badge should show "Connected" (green)

### 3. Test Connection
```bash
node test-connection.js
```

## Troubleshooting

### Backend won't start
- Check Python version: `python --version` (needs 3.11+)
- Install dependencies: `pip install -r requirements.txt`
- Check port 8000 is available

### Frontend won't start
- Check Node.js version: `node --version` (needs 16+)
- Install dependencies: `npm install`
- Check port 3000 is available

### Connection fails
- Verify both servers are running
- Check firewall settings
- Verify CORS configuration in backend
- Check browser console for errors

## Default Ports

- **Backend:** http://localhost:8000
- **Frontend:** http://localhost:3000

## Environment Variables

### Backend
Create `.env` in `backend/` directory (optional):
```
EMBEDDING_MODEL=all-MiniLM-L6-v2
LLM_MODEL=microsoft/DialoGPT-medium
DATABASE_URL=sqlite:///./support_copilot.db
```

### Frontend
Create `.env` in `frontend/` directory (optional):
```
REACT_APP_API_URL=http://localhost:8000
```

## Production

For production deployment, update:
- CORS origins in backend to your frontend domain
- API URL in frontend to your backend domain
- Use environment variables for configuration

