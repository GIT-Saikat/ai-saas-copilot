/**
 * Connection test utilities for frontend-backend communication
 */

import apiService from '../services/api';

export interface ConnectionTestResult {
  success: boolean;
  message: string;
  details?: any;
}

/**
 * Test connection to backend API
 */
export async function testBackendConnection(): Promise<ConnectionTestResult> {
  try {
    const health = await apiService.healthCheck();
    return {
      success: true,
      message: `Backend is ${health.status}`,
      details: health,
    };
  } catch (error: any) {
    return {
      success: false,
      message: error.message || 'Cannot connect to backend',
      details: error,
    };
  }
}

/**
 * Test all API endpoints
 */
export async function testAllEndpoints(): Promise<{
  health: ConnectionTestResult;
  analytics: ConnectionTestResult;
}> {
  const results = {
    health: await testBackendConnection(),
    analytics: { success: false, message: 'Not tested' } as ConnectionTestResult,
  };

  // Test analytics endpoint
  try {
    await apiService.getAnalytics();
    results.analytics = {
      success: true,
      message: 'Analytics endpoint working',
    };
  } catch (error: any) {
    results.analytics = {
      success: false,
      message: error.message || 'Analytics endpoint failed',
    };
  }

  return results;
}

