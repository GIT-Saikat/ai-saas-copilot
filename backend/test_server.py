"""
Test script to verify backend server is working.
"""

import requests
import time
import json

def test_server():
    """Test if server is running and endpoints work."""
    base_url = "http://localhost:8000"
    
    print("=" * 60)
    print("Testing Backend Server")
    print("=" * 60)
    
    # Wait for server to start
    print("\nWaiting for server to start...")
    max_attempts = 10
    for i in range(max_attempts):
        try:
            response = requests.get(f"{base_url}/api/health", timeout=2)
            if response.status_code == 200:
                print(f"[OK] Server is running! (attempt {i+1})")
                break
        except requests.exceptions.ConnectionError:
            if i < max_attempts - 1:
                print(f"  Waiting... ({i+1}/{max_attempts})")
                time.sleep(2)
            else:
                print("[ERROR] Server is not responding")
                print("\nPlease start the server first:")
                print("  cd backend")
                print("  python run_server.py")
                return False
        except Exception as e:
            print(f"[ERROR] {e}")
            return False
    
    # Test 1: Health Check
    print("\n1. Testing Health Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/health")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
        assert response.status_code == 200
        print("   [OK] Health check passed")
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 2: Query Endpoint
    print("\n2. Testing Query Endpoint...")
    try:
        query_data = {"query": "How do I create an account?"}
        response = requests.post(f"{base_url}/api/query", json=query_data)
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Answer length: {len(result.get('answer', ''))} chars")
        print(f"   Confidence: {result.get('confidence', 0):.3f}")
        print(f"   Blocked: {result.get('blocked', False)}")
        print(f"   Chunks: {len(result.get('chunks', []))}")
        print(f"   Response time: {result.get('response_time_ms', 0):.2f}ms")
        assert response.status_code == 200
        assert 'answer' in result
        print("   [OK] Query endpoint working")
    except Exception as e:
        print(f"   [ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Analytics Endpoint
    print("\n3. Testing Analytics Endpoint...")
    try:
        response = requests.get(f"{base_url}/api/analytics")
        print(f"   Status: {response.status_code}")
        result = response.json()
        print(f"   Total queries: {result.get('total_queries', 0)}")
        print(f"   Avg confidence: {result.get('avg_confidence', 0):.3f}")
        assert response.status_code == 200
        print("   [OK] Analytics endpoint working")
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False
    
    # Test 4: API Documentation
    print("\n4. Testing API Documentation...")
    try:
        response = requests.get(f"{base_url}/docs")
        print(f"   Status: {response.status_code}")
        assert response.status_code == 200
        print("   [OK] API docs available at http://localhost:8000/docs")
    except Exception as e:
        print(f"   [WARNING] {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print("[SUCCESS] Backend server is working correctly!")
    print(f"\nAPI Endpoints:")
    print(f"  - Health: {base_url}/api/health")
    print(f"  - Query: {base_url}/api/query")
    print(f"  - Analytics: {base_url}/api/analytics")
    print(f"  - Docs: {base_url}/docs")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_server()
    exit(0 if success else 1)

