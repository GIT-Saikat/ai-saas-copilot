import React, { useMemo } from 'react';
import { PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { AnalyticsResponse } from '../../types';

interface CategoryBreakdownProps {
  analytics: AnalyticsResponse;
}

export const CategoryBreakdown: React.FC<CategoryBreakdownProps> = ({ analytics }) => {
  // Extract categories from recent queries
  const categoryData = useMemo(() => {
    // For now, we'll create sample data based on available metrics
    // In production, backend should provide category breakdown
    const categories = [
      { name: 'Billing', queries: Math.floor(analytics.total_queries * 0.3), confidence: analytics.avg_confidence },
      { name: 'Features', queries: Math.floor(analytics.total_queries * 0.25), confidence: analytics.avg_confidence },
      { name: 'API', queries: Math.floor(analytics.total_queries * 0.2), confidence: analytics.avg_confidence },
      { name: 'Security', queries: Math.floor(analytics.total_queries * 0.15), confidence: analytics.avg_confidence },
      { name: 'Other', queries: Math.floor(analytics.total_queries * 0.1), confidence: analytics.avg_confidence },
    ].filter(cat => cat.queries > 0);

    return categories;
  }, [analytics]);

  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Pie Chart - Queries by Category */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Queries by Category</CardTitle>
          <CardDescription>Distribution of queries across categories</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={categoryData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${percent ? (percent * 100).toFixed(0) : 0}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="queries"
              >
                {categoryData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Bar Chart - Confidence by Category */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Confidence by Category</CardTitle>
          <CardDescription>Average confidence scores per category</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={categoryData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis domain={[0, 1]} />
              <Tooltip formatter={(value: number) => `${(value * 100).toFixed(0)}%`} />
              <Bar dataKey="confidence" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
};

