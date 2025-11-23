import axios from 'axios';
import { QueryResponse, FeedbackRequest, AnalyticsResponse, HealthResponse } from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// Add auth token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export class ApiService {
  /**
   * Submit a query to the RAG system
   */
  async query(question: string, userSessionId?: string): Promise<QueryResponse> {
    try {
      const response = await api.post<QueryResponse>('/api/query', {
        query: question,
        user_session_id: userSessionId,
      });
      return response.data;
    } catch (error: any) {
      // Handle timeout
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        throw new Error('Request timeout: The server took too long to respond. Please try again.');
      }
      // Handle network errors
      if (error.request && !error.response) {
        throw new Error('Network error: Could not connect to server. Please check your connection.');
      }
      // Handle validation errors (400)
      if (error.response?.status === 400) {
        throw new Error(error.response.data.detail || 'Invalid request. Please check your input.');
      }
      // Handle server errors (500+)
      if (error.response?.status >= 500) {
        throw new Error('Server error: Please try again later.');
      }
      // Handle other errors
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to process query');
      }
      throw new Error('Network error: Could not connect to server');
    }
  }

  /**
   * Submit feedback for a query
   */
  async submitFeedback(queryId: number, feedback: 'positive' | 'negative'): Promise<void> {
    try {
      const request: FeedbackRequest = { query_id: queryId, feedback };
      await api.post('/api/feedback', request);
    } catch (error: any) {
      // Handle timeout
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        throw new Error('Request timeout: Please try again.');
      }
      // Handle network errors
      if (error.request && !error.response) {
        throw new Error('Network error: Could not submit feedback. Please check your connection.');
      }
      // Handle validation errors
      if (error.response?.status === 400) {
        throw new Error(error.response.data.detail || 'Invalid feedback. Please try again.');
      }
      // Handle other errors
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to submit feedback');
      }
      throw new Error('Network error: Could not submit feedback');
    }
  }

  /**
   * Get analytics data
   */
  async getAnalytics(): Promise<AnalyticsResponse> {
    try {
      const response = await api.get<AnalyticsResponse>('/api/analytics');
      return response.data;
    } catch (error: any) {
      if (error.response) {
        throw new Error(error.response.data.detail || 'Failed to fetch analytics');
      }
      throw new Error('Network error: Could not fetch analytics');
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<HealthResponse> {
    try {
      const response = await api.get<HealthResponse>('/api/health');
      return response.data;
    } catch (error: any) {
      throw new Error('Health check failed');
    }
  }
}

const apiService = new ApiService();
export default apiService;

