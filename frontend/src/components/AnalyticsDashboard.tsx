import React, { useEffect, useState } from 'react';
import { BarChart3 } from 'lucide-react';
import { Card, CardContent } from './ui/card';
import { StatsBar } from './StatsBar';
import { TimeSeriesCharts } from './analytics/TimeSeriesCharts';
import { CategoryBreakdown } from './analytics/CategoryBreakdown';
import { RecentQueriesTable } from './analytics/RecentQueriesTable';
import { AlertsSection } from './analytics/AlertsSection';
import { ActionableInsights } from './analytics/ActionableInsights';
import { AnalyticsResponse } from '../types';
import apiService from '../services/api';

export const AnalyticsDashboard: React.FC = () => {
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
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
  }, []);

  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-muted-foreground">Loading analytics dashboard...</div>
        </CardContent>
      </Card>
    );
  }

  if (error || !analytics) {
    return (
      <Card>
        <CardContent className="pt-6">
          <div className="text-center text-destructive">
            Failed to load analytics: {error || 'Unknown error'}
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-2">
        <BarChart3 className="h-6 w-6" />
        <h2 className="text-2xl font-bold">Analytics Dashboard</h2>
      </div>

      {/* Overview Cards (Step 6.2.1) */}
      <StatsBar analytics={analytics} />

      {/* Time Series Charts */}
      <TimeSeriesCharts analytics={analytics} />

      {/* Category Breakdown */}
      <CategoryBreakdown analytics={analytics} />

      {/* Alerts and Insights Side by Side */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <AlertsSection analytics={analytics} />
        <ActionableInsights analytics={analytics} />
      </div>

      {/* Recent Queries Table */}
      <RecentQueriesTable analytics={analytics} />
    </div>
  );
};

