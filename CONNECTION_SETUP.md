# Frontend-Backend Connection Setup Guide

## Quick Start

### 1. Start the Backend Server

```bash
cd backend
python run_server.py
```

The backend will start on **http://localhost:8000**

You should see:
```
Starting FastAPI server on http://localhost:8000
API Documentation: http://localhost:8000/docs
Health Check: http://localhost:8000/api/health
```

### 2. Start the Frontend Development Server

```bash
cd frontend
npm start
```

The frontend will start on **http://localhost:3000**

### 3. Verify Connection

- Check the **Connection Status** badge in the top-right corner of the frontend
- It should show "Connected" with a green indicator
- If it shows "Disconnected", check the troubleshooting section below

## Configuration

### Backend Configuration

**Port:** 8000 (default)
**CORS:** Configured to allow all origins (`*`) for development

**Location:** `backend/app/main.py`
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend Configuration

**API Base URL:** `http://localhost:8000` (default)

**Location:** `frontend/src/services/api.ts`
```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

**To change the API URL:**
Create a `.env` file in the `frontend` directory:
```
REACT_APP_API_URL=http://localhost:8000
```

## API Endpoints

The frontend communicates with these backend endpoints:

1. **Health Check:** `GET /api/health`
   - Used for connection status
   - Returns system health

2. **Query:** `POST /api/query`
   - Main query endpoint
   - Requires: `{ "query": "user question" }`

3. **Feedback:** `POST /api/feedback`
   - Submit feedback
   - Requires: `{ "query_id": 123, "feedback": "positive|negative" }`

4. **Analytics:** `GET /api/analytics`
   - Get analytics data
   - Returns dashboard metrics

## Connection Status Indicator

The frontend includes a **ConnectionStatus** component that:
- Shows connection status in the header
- Automatically checks connection every 30 seconds
- Displays error messages if connection fails
- Shows "Connected" (green) or "Disconnected" (red)

## Troubleshooting

### Issue: Frontend shows "Disconnected"

**Possible causes:**

1. **Backend not running**
   - Solution: Start the backend server
   - Check: `http://localhost:8000/api/health` in browser

2. **Port conflict**
   - Solution: Check if port 8000 is already in use
   - Windows: `netstat -ano | findstr :8000`
   - Linux/Mac: `lsof -i :8000`

3. **CORS issues**
   - Solution: Backend CORS is already configured, but check if middleware order is correct

4. **Wrong API URL**
   - Solution: Check `.env` file or verify `API_BASE_URL` in `api.ts`

5. **Firewall blocking**
   - Solution: Allow port 8000 in firewall settings

### Issue: CORS errors in browser console

**Error:** `Access to XMLHttpRequest at 'http://localhost:8000/...' from origin 'http://localhost:3000' has been blocked by CORS policy`

**Solution:**
- Backend CORS is configured, but ensure the backend server is running
- Check that `CORSMiddleware` is added before other middleware
- Verify `allow_origins=["*"]` is set (for development)

### Issue: Network errors

**Error:** `Network error: Could not connect to server`

**Solution:**
1. Verify backend is running: `curl http://localhost:8000/api/health`
2. Check backend logs for errors
3. Verify no proxy is interfering
4. Try accessing `http://localhost:8000/docs` in browser

### Issue: Timeout errors

**Error:** `Request timeout: The server took too long to respond`

**Solution:**
- Backend might be processing a heavy request
- Check backend logs
- Increase timeout in `api.ts` if needed (currently 30 seconds)

## Testing the Connection

### Manual Test

1. Open browser console (F12)
2. Go to Network tab
3. Submit a query in the frontend
4. Check if request to `http://localhost:8000/api/query` succeeds

### Programmatic Test

Use the connection test utility:
```typescript
import { testBackendConnection } from './utils/connectionTest';

const result = await testBackendConnection();
console.log(result);
```

## Production Setup

For production, update CORS to allow only your frontend domain:

```python
# backend/app/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

And set the frontend API URL:
```
REACT_APP_API_URL=https://your-backend-domain.com
```

## Verification Checklist

- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 3000
- [ ] Connection status shows "Connected"
- [ ] Can submit queries successfully
- [ ] Analytics dashboard loads data
- [ ] Feedback submission works
- [ ] No CORS errors in browser console
- [ ] Health check endpoint accessible

## Next Steps

Once connected:
1. Test query submission
2. Check analytics dashboard
3. Submit feedback
4. Verify all features work end-to-end

