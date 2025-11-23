/**
 * Simple script to test frontend-backend connection
 * Run with: node test-connection.js
 */

const axios = require('axios');

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

async function testConnection() {
  console.log('🔍 Testing Frontend-Backend Connection...\n');
  console.log(`Backend URL: ${API_BASE_URL}\n`);

  // Test 1: Health Check
  console.log('1. Testing Health Check Endpoint...');
  try {
    const healthResponse = await axios.get(`${API_BASE_URL}/api/health`);
    console.log('   ✅ Health Check: SUCCESS');
    console.log(`   Status: ${healthResponse.data.status}`);
    console.log(`   Version: ${healthResponse.data.version}\n`);
  } catch (error) {
    console.log('   ❌ Health Check: FAILED');
    console.log(`   Error: ${error.message}\n`);
    console.log('   💡 Make sure the backend server is running!');
    console.log('   Run: cd backend && python run_server.py\n');
    return false;
  }

  // Test 2: Analytics Endpoint
  console.log('2. Testing Analytics Endpoint...');
  try {
    const analyticsResponse = await axios.get(`${API_BASE_URL}/api/analytics`);
    console.log('   ✅ Analytics: SUCCESS');
    console.log(`   Total Queries: ${analyticsResponse.data.total_queries}\n`);
  } catch (error) {
    console.log('   ⚠️  Analytics: FAILED (may be expected if no data)');
    console.log(`   Error: ${error.message}\n`);
  }

  // Test 3: Query Endpoint
  console.log('3. Testing Query Endpoint...');
  try {
    const queryResponse = await axios.post(`${API_BASE_URL}/api/query`, {
      query: 'test connection'
    });
    console.log('   ✅ Query: SUCCESS');
    console.log(`   Answer received: ${queryResponse.data.answer.substring(0, 50)}...\n`);
  } catch (error) {
    console.log('   ⚠️  Query: FAILED (may be expected if RAG not initialized)');
    console.log(`   Error: ${error.response?.data?.detail || error.message}\n`);
  }

  console.log('✅ Connection test completed!');
  console.log('\n📝 Next Steps:');
  console.log('   1. Start backend: cd backend && python run_server.py');
  console.log('   2. Start frontend: cd frontend && npm start');
  console.log('   3. Open http://localhost:3000 in your browser');
  console.log('   4. Check the connection status badge in the header\n');

  return true;
}

testConnection().catch(console.error);

