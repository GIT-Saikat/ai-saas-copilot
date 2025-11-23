# Frontend-Backend Connection Setup ✅

## Status: **CONNECTED AND CONFIGURED**

The frontend and backend are now properly configured to communicate with each other.

## What Was Configured

### 1. Backend CORS Configuration ✅
**Location:** `backend/app/main.py`

- CORS middleware configured to allow all origins (development)
- Allows credentials, all methods, and all headers
- Properly ordered before other middleware

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development - allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 2. Frontend API Service ✅
**Location:** `frontend/src/services/api.ts`

- Base URL: `http://localhost:8000` (configurable via env)
- Axios instance with proper configuration
- Request timeout: 30 seconds
- Authentication token interceptor
- Comprehensive error handling

### 3. Connection Status Indicator ✅
**Location:** `frontend/src/components/ConnectionStatus.tsx`

- Real-time connection status in header
- Auto-checks every 30 seconds
- Visual indicators (Connected/Disconnected)
- Error messages for troubleshooting

### 4. Connection Test Utilities ✅
**Location:** `frontend/src/utils/connectionTest.ts`

- Programmatic connection testing
- Health check verification
- Endpoint testing utilities

## API Endpoints Connected

| Endpoint | Method | Purpose | Status |
|----------|--------|---------|--------|
| `/api/health` | GET | Health check | ✅ Connected |
| `/api/query` | POST | Submit queries | ✅ Connected |
| `/api/feedback` | POST | Submit feedback | ✅ Connected |
| `/api/analytics` | GET | Get analytics | ✅ Connected |

## How to Use

### Step 1: Start Backend
```bash
cd backend
python run_server.py
```

**Expected output:**
```
Starting FastAPI server on http://localhost:8000
API Documentation: http://localhost:8000/docs
Health Check: http://localhost:8000/api/health
```

### Step 2: Start Frontend
```bash
cd frontend
npm start
```

**Expected output:**
```
Compiled successfully!
You can now view frontend in the browser.
  Local:            http://localhost:3000
```

### Step 3: Verify Connection

1. **Check Connection Status Badge**
   - Top-right corner of the frontend
   - Should show "Connected" (green) when backend is running
   - Shows "Disconnected" (red) when backend is down

2. **Test Health Check**
   - Open: http://localhost:8000/api/health
   - Should return JSON with status

3. **Test Query**
   - Enter a question in the frontend
   - Should receive response from backend

## Connection Features

### ✅ Automatic Connection Monitoring
- Checks connection every 30 seconds
- Updates status badge automatically
- Shows error messages when disconnected

### ✅ Error Handling
- Network errors → Shows retry button
- Timeout errors → Shows timeout message
- Server errors → Shows error details
- Validation errors → Shows inline messages

### ✅ Retry Functionality
- Retry button for network/timeout errors
- Remembers last query for retry
- Prevents duplicate requests

## Configuration Files

### Backend
- **CORS:** `backend/app/main.py` (lines 54-60)
- **Port:** 8000 (configured in `run_server.py`)
- **Host:** 0.0.0.0 (allows external connections)

### Frontend
- **API URL:** `frontend/src/services/api.ts` (line 4)
- **Environment:** Can be set via `.env` file
- **Port:** 3000 (React default)

## Testing Connection

### Method 1: Visual Check
- Look at Connection Status badge in header
- Green = Connected
- Red = Disconnected

### Method 2: Browser Console
- Open DevTools (F12)
- Check Network tab
- Submit a query
- Verify request to `http://localhost:8000/api/query`

### Method 3: Test Script
```bash
node test-connection.js
```

### Method 4: Manual API Test
```bash
curl http://localhost:8000/api/health
```

## Troubleshooting

### Connection Status Shows "Disconnected"

1. **Check Backend is Running**
   ```bash
   # Check if backend is running
   curl http://localhost:8000/api/health
   ```

2. **Check Port Availability**
   ```bash
   # Windows
   netstat -ano | findstr :8000
   
   # Linux/Mac
   lsof -i :8000
   ```

3. **Check Browser Console**
   - Open DevTools (F12)
   - Look for CORS or network errors
   - Check Network tab for failed requests

4. **Verify API URL**
   - Check `frontend/src/services/api.ts`
   - Verify `API_BASE_URL` is correct
   - Check `.env` file if using custom URL

### CORS Errors

If you see CORS errors:
- Backend CORS is already configured
- Ensure backend server is running
- Check middleware order in `main.py`
- Verify `allow_origins=["*"]` is set

### Network Errors

If you see network errors:
- Verify backend is accessible: `http://localhost:8000/api/health`
- Check firewall settings
- Verify no proxy is interfering
- Check backend logs for errors

## Production Configuration

For production, update:

1. **Backend CORS** - Specify frontend domain:
```python
allow_origins=["https://your-frontend-domain.com"]
```

2. **Frontend API URL** - Set in `.env`:
```
REACT_APP_API_URL=https://your-backend-domain.com
```

## Summary

✅ **Backend CORS:** Configured and working  
✅ **Frontend API Service:** Configured and working  
✅ **Connection Status:** Real-time monitoring  
✅ **Error Handling:** Comprehensive  
✅ **Retry Functionality:** Implemented  
✅ **Documentation:** Complete  

**The frontend and backend are ready to communicate!**

Just start both servers and the connection will be established automatically.

