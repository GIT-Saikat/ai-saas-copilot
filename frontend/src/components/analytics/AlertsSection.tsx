import React, { useMemo } from 'react';
import { AlertTriangle, TrendingDown, Clock, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription, AlertTitle } from '../ui/alert';
import { AnalyticsResponse } from '../../types';

interface AlertsSectionProps {
  analytics: AnalyticsResponse;
}

export const AlertsSection: React.FC<AlertsSectionProps> = ({ analytics }) => {
  const alerts = useMemo(() => {
    const alertList: Array<{ type: 'warning' | 'error' | 'info'; title: string; message: string; icon: React.ReactNode }> = [];

    // Check blocked query rate
    const blockedRate = analytics.total_queries > 0
      ? (analytics.blocked_queries / analytics.total_queries) * 100
      : 0;

    if (blockedRate > 15) {
      alertList.push({
        type: 'warning',
        title: 'High Blocked Query Rate',
        message: `${blockedRate.toFixed(1)}% of queries are being blocked. Consider expanding documentation coverage or lowering the similarity threshold.`,
        icon: <AlertTriangle className="h-4 w-4" />,
      });
    }

    // Check negative feedback rate
    const totalFeedback = analytics.positive_feedback + analytics.negative_feedback;
    const negativeRate = totalFeedback > 0
      ? (analytics.negative_feedback / totalFeedback) * 100
      : 0;

    if (negativeRate > 30) {
      alertList.push({
        type: 'error',
        title: 'High Negative Feedback Rate',
        message: `${negativeRate.toFixed(1)}% of feedback is negative. Review answer quality and improve documentation for frequently asked questions.`,
        icon: <TrendingDown className="h-4 w-4" />,
      });
    }

    // Check response time
    if (analytics.avg_response_time_ms > 3000) {
      alertList.push({
        type: 'warning',
        title: 'Slow Response Times',
        message: `Average response time is ${(analytics.avg_response_time_ms / 1000).toFixed(1)}s. Consider optimizing the RAG pipeline or scaling infrastructure.`,
        icon: <Clock className="h-4 w-4" />,
      });
    }

    // Check low confidence
    if (analytics.avg_confidence < 0.65) {
      alertList.push({
        type: 'warning',
        title: 'Low Average Confidence',
        message: `Average confidence is ${(analytics.avg_confidence * 100).toFixed(0)}%. Documentation may need improvement or the similarity threshold may be too high.`,
        icon: <AlertCircle className="h-4 w-4" />,
      });
    }

    return alertList;
  }, [analytics]);

  if (alerts.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">System Health</CardTitle>
        </CardHeader>
        <CardContent>
          <Alert>
            <AlertCircle className="h-4 w-4 text-green-600" />
            <AlertTitle>All Systems Operational</AlertTitle>
            <AlertDescription>
              No issues detected. All metrics are within acceptable ranges.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Alerts & Warnings</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {alerts.map((alert, index) => (
          <Alert
            key={index}
            variant={alert.type === 'error' ? 'destructive' : 'default'}
          >
            {alert.icon}
            <AlertTitle>{alert.title}</AlertTitle>
            <AlertDescription>{alert.message}</AlertDescription>
          </Alert>
        ))}
      </CardContent>
    </Card>
  );
};

