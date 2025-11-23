import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { AnalyticsResponse } from '../../types';

interface TimeSeriesChartsProps {
  analytics: AnalyticsResponse;
}

export const TimeSeriesCharts: React.FC<TimeSeriesChartsProps> = ({ analytics }) => {
  // For now, we'll create sample data structure
  // In production, this would come from backend with time series data
  const sampleTimeSeriesData = [
    { date: 'Day 1', queries: analytics.total_queries > 0 ? Math.floor(analytics.total_queries * 0.1) : 0, confidence: analytics.avg_confidence, responseTime: analytics.avg_response_time_ms },
    { date: 'Day 2', queries: analytics.total_queries > 0 ? Math.floor(analytics.total_queries * 0.15) : 0, confidence: analytics.avg_confidence, responseTime: analytics.avg_response_time_ms },
    { date: 'Day 3', queries: analytics.total_queries > 0 ? Math.floor(analytics.total_queries * 0.2) : 0, confidence: analytics.avg_confidence, responseTime: analytics.avg_response_time_ms },
    { date: 'Day 4', queries: analytics.total_queries > 0 ? Math.floor(analytics.total_queries * 0.25) : 0, confidence: analytics.avg_confidence, responseTime: analytics.avg_response_time_ms },
    { date: 'Day 5', queries: analytics.total_queries > 0 ? Math.floor(analytics.total_queries * 0.3) : 0, confidence: analytics.avg_confidence, responseTime: analytics.avg_response_time_ms },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Queries Over Time */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Queries Over Time</CardTitle>
          <CardDescription>Daily query volume</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <AreaChart data={sampleTimeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area type="monotone" dataKey="queries" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.6} />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Confidence Scores Over Time */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Confidence Scores Over Time</CardTitle>
          <CardDescription>Average confidence trend</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={sampleTimeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis domain={[0, 1]} />
              <Tooltip formatter={(value: number) => `${(value * 100).toFixed(0)}%`} />
              <Line type="monotone" dataKey="confidence" stroke="#10b981" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Response Times Over Time */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle className="text-lg">Response Times Over Time</CardTitle>
          <CardDescription>Average response time in milliseconds</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={sampleTimeSeriesData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip formatter={(value: number) => `${value.toFixed(0)}ms`} />
              <Line type="monotone" dataKey="responseTime" stroke="#f59e0b" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

