import React, { useState, useMemo } from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown, Eye } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { AnalyticsResponse } from '../../types';
import { cn } from '../../lib/utils';

interface RecentQueriesTableProps {
  analytics: AnalyticsResponse;
}

type SortField = 'query' | 'confidence' | 'feedback' | 'created_at';
type SortDirection = 'asc' | 'desc';

export const RecentQueriesTable: React.FC<RecentQueriesTableProps> = ({ analytics }) => {
  const [sortField, setSortField] = useState<SortField>('created_at');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');
  const [expandedRow, setExpandedRow] = useState<number | null>(null);

  const sortedQueries = useMemo(() => {
    const queries = [...analytics.recent_queries];
    
    queries.sort((a, b) => {
      let aValue: any;
      let bValue: any;

      switch (sortField) {
        case 'query':
          aValue = a.query.toLowerCase();
          bValue = b.query.toLowerCase();
          break;
        case 'confidence':
          aValue = a.confidence;
          bValue = b.confidence;
          break;
        case 'feedback':
          aValue = a.feedback || '';
          bValue = b.feedback || '';
          break;
        case 'created_at':
          aValue = new Date(a.created_at).getTime();
          bValue = new Date(b.created_at).getTime();
          break;
        default:
          return 0;
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return queries;
  }, [analytics.recent_queries, sortField, sortDirection]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
    if (confidence >= 0.65) return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
    return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
  };

  const SortButton: React.FC<{ field: SortField; children: React.ReactNode }> = ({ field, children }) => (
    <Button
      variant="ghost"
      size="sm"
      className="h-8 gap-1"
      onClick={() => handleSort(field)}
    >
      {children}
      {sortField === field ? (
        sortDirection === 'asc' ? (
          <ArrowUp className="h-3 w-3" />
        ) : (
          <ArrowDown className="h-3 w-3" />
        )
      ) : (
        <ArrowUpDown className="h-3 w-3 opacity-50" />
      )}
    </Button>
  );

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-lg">Recent Queries</CardTitle>
        <CardDescription>Last {analytics.recent_queries.length} queries with details</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left p-2">
                  <SortButton field="query">Query</SortButton>
                </th>
                <th className="text-left p-2">
                  <SortButton field="confidence">Confidence</SortButton>
                </th>
                <th className="text-left p-2">
                  <SortButton field="feedback">Feedback</SortButton>
                </th>
                <th className="text-left p-2">
                  <SortButton field="created_at">Time</SortButton>
                </th>
                <th className="text-left p-2">Actions</th>
              </tr>
            </thead>
            <tbody>
              {sortedQueries.length === 0 ? (
                <tr>
                  <td colSpan={5} className="text-center p-8 text-muted-foreground">
                    No queries yet
                  </td>
                </tr>
              ) : (
                sortedQueries.map((query) => (
                  <React.Fragment key={query.id}>
                    <tr className="border-b hover:bg-accent/50">
                      <td className="p-2 max-w-xs truncate" title={query.query}>
                        {query.query}
                      </td>
                      <td className="p-2">
                        <Badge
                          variant="outline"
                          className={cn(getConfidenceColor(query.confidence))}
                        >
                          {(query.confidence * 100).toFixed(0)}%
                        </Badge>
                      </td>
                      <td className="p-2">
                        {query.feedback ? (
                          <Badge
                            variant={query.feedback === 'positive' ? 'default' : 'destructive'}
                          >
                            {query.feedback}
                          </Badge>
                        ) : (
                          <span className="text-muted-foreground text-sm">No feedback</span>
                        )}
                      </td>
                      <td className="p-2 text-sm text-muted-foreground">
                        {new Date(query.created_at).toLocaleString()}
                      </td>
                      <td className="p-2">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setExpandedRow(expandedRow === query.id ? null : query.id)}
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      </td>
                    </tr>
                    {expandedRow === query.id && (
                      <tr>
                        <td colSpan={5} className="p-4 bg-accent/30">
                          <div className="space-y-2">
                            <div>
                              <strong>Full Query:</strong> {query.query}
                            </div>
                            <div className="grid grid-cols-2 gap-4 text-sm">
                              <div>
                                <strong>Confidence:</strong> {(query.confidence * 100).toFixed(2)}%
                              </div>
                              <div>
                                <strong>Feedback:</strong> {query.feedback || 'None'}
                              </div>
                              <div>
                                <strong>Created:</strong> {new Date(query.created_at).toLocaleString()}
                              </div>
                              <div>
                                <strong>ID:</strong> {query.id}
                              </div>
                            </div>
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                ))
              )}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
};

