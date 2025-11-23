import React, { useMemo } from 'react';
import { Lightbulb, TrendingUp, FileText, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Badge } from '../ui/badge';
import { AnalyticsResponse } from '../../types';

interface ActionableInsightsProps {
  analytics: AnalyticsResponse;
}

export const ActionableInsights: React.FC<ActionableInsightsProps> = ({ analytics }) => {
  const insights = useMemo(() => {
    const insightList: Array<{ type: 'improvement' | 'warning' | 'info'; title: string; description: string; icon: React.ReactNode; priority: 'high' | 'medium' | 'low' }> = [];

    // Blocked query rate insight
    const blockedRate = analytics.total_queries > 0
      ? (analytics.blocked_queries / analytics.total_queries) * 100
      : 0;

    if (blockedRate > 15) {
      insightList.push({
        type: 'improvement',
        title: 'Expand Documentation Coverage',
        description: `With ${blockedRate.toFixed(1)}% of queries being blocked, consider adding documentation for the top blocked query topics.`,
        icon: <FileText className="h-5 w-5" />,
        priority: 'high',
      });
    }

    // Negative feedback insight
    const totalFeedback = analytics.positive_feedback + analytics.negative_feedback;
    const negativeRate = totalFeedback > 0
      ? (analytics.negative_feedback / totalFeedback) * 100
      : 0;

    if (negativeRate > 30) {
      insightList.push({
        type: 'warning',
        title: 'Review Answer Quality',
        description: `${negativeRate.toFixed(1)}% negative feedback indicates quality issues. Review answers for categories with low satisfaction.`,
        icon: <TrendingUp className="h-5 w-5" />,
        priority: 'high',
      });
    }

    // Confidence trend insight
    if (analytics.avg_confidence < 0.75) {
      insightList.push({
        type: 'info',
        title: 'Documentation Refresh Recommended',
        description: `Average confidence of ${(analytics.avg_confidence * 100).toFixed(0)}% suggests documentation may be outdated. Consider a refresh schedule.`,
        icon: <RefreshCw className="h-5 w-5" />,
        priority: 'medium',
      });
    }

    // Response time insight
    if (analytics.avg_response_time_ms > 2000) {
      insightList.push({
        type: 'info',
        title: 'Consider Infrastructure Scaling',
        description: `Average response time of ${(analytics.avg_response_time_ms / 1000).toFixed(1)}s may impact user experience. Consider scaling infrastructure or optimizing the pipeline.`,
        icon: <TrendingUp className="h-5 w-5" />,
        priority: 'medium',
      });
    }

    // Positive insight
    if (analytics.avg_confidence >= 0.8 && negativeRate < 20) {
      insightList.push({
        type: 'info',
        title: 'System Performing Well',
        description: `High confidence (${(analytics.avg_confidence * 100).toFixed(0)}%) and low negative feedback (${negativeRate.toFixed(0)}%) indicate the system is working effectively.`,
        icon: <Lightbulb className="h-5 w-5" />,
        priority: 'low',
      });
    }

    return insightList.sort((a, b) => {
      const priorityOrder = { high: 0, medium: 1, low: 2 };
      return priorityOrder[a.priority] - priorityOrder[b.priority];
    });
  }, [analytics]);

  if (insights.length === 0) {
    return null;
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case 'low':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200';
      default:
        return '';
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg flex items-center gap-2">
          <Lightbulb className="h-5 w-5" />
          Actionable Insights
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {insights.map((insight, index) => (
          <div
            key={index}
            className="flex items-start gap-4 p-4 border rounded-lg hover:bg-accent/50 transition-colors"
          >
            <div className="mt-1">{insight.icon}</div>
            <div className="flex-1 space-y-1">
              <div className="flex items-center gap-2">
                <h4 className="font-semibold">{insight.title}</h4>
                <Badge
                  variant="outline"
                  className={getPriorityColor(insight.priority)}
                >
                  {insight.priority}
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground">{insight.description}</p>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
};

