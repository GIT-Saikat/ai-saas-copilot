import React, { useEffect, useState } from 'react';
import { BarChart3, TrendingUp, Clock, MessageSquare, XCircle, CheckCircle2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { AnalyticsResponse } from '../types';
import apiService from '../services/api';

interface StatsBarProps {
  analytics?: AnalyticsResponse; // Optional prop to avoid duplicate API calls
}

export const StatsBar: React.FC<StatsBarProps> = ({ analytics: providedAnalytics }) => {
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(providedAnalytics || null);
  const [loading, setLoading] = useState(!providedAnalytics);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    // If analytics provided as prop, use it and don't fetch
    if (providedAnalytics) {
      setAnalytics(providedAnalytics);
      setLoading(false);
      return;
    }

    // Otherwise, fetch analytics
    const fetchAnalytics = async () => {
      try {
        setLoading(true);
        const data = await apiService.getAnalytics();
        setAnalytics(data);
        setError(null);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchAnalytics();
    // Refresh every 30 seconds
    const interval = setInterval(fetchAnalytics, 30000);
    return () => clearInterval(interval);
  }, [providedAnalytics]);

  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-muted-foreground">Loading analytics...</div>
        </CardContent>
      </Card>
    );
  }

  if (error || !analytics) {
    return null; // Silently fail - analytics are optional
  }

  const feedbackRatio = analytics.total_queries > 0
    ? ((analytics.positive_feedback / (analytics.positive_feedback + analytics.negative_feedback)) * 100).toFixed(0)
    : '0';

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <BarChart3 className="h-5 w-5" />
          Analytics Overview
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <MessageSquare className="h-4 w-4" />
              Total Queries
            </div>
            <div className="text-2xl font-bold">{analytics.total_queries}</div>
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <TrendingUp className="h-4 w-4" />
              Avg Confidence
            </div>
            <div className="text-2xl font-bold">
              {(analytics.avg_confidence * 100).toFixed(0)}%
            </div>
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <XCircle className="h-4 w-4" />
              Blocked
            </div>
            <div className="text-2xl font-bold text-red-600">
              {analytics.blocked_queries}
            </div>
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <CheckCircle2 className="h-4 w-4" />
              Positive
            </div>
            <div className="text-2xl font-bold text-green-600">
              {analytics.positive_feedback}
            </div>
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <XCircle className="h-4 w-4" />
              Negative
            </div>
            <div className="text-2xl font-bold text-red-600">
              {analytics.negative_feedback}
            </div>
          </div>

          <div className="space-y-1">
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Clock className="h-4 w-4" />
              Avg Response
            </div>
            <div className="text-2xl font-bold">
              {analytics.avg_response_time_ms.toFixed(0)}ms
            </div>
          </div>
        </div>

        {analytics.total_queries > 0 && (
          <div className="mt-4 pt-4 border-t">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">Feedback Ratio</span>
              <Badge variant="outline" className="text-base px-3 py-1">
                {feedbackRatio}% positive
              </Badge>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

