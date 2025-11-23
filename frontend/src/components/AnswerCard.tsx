import React from 'react';
import { CheckCircle2, XCircle, Clock, AlertCircle } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Alert, AlertDescription, AlertTitle } from './ui/alert';
import { cn } from '../lib/utils';
import { QueryResponse } from '../types';

interface AnswerCardProps {
  response: QueryResponse | null;
  loading?: boolean;
}

export const AnswerCard: React.FC<AnswerCardProps> = ({ response, loading }) => {
  if (loading) {
    return (
      <Card className="w-full">
        <CardContent className="pt-6">
          <div className="flex items-center justify-center py-8">
            <div className="animate-pulse text-muted-foreground">Processing your query...</div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!response) {
    return null;
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'bg-green-100 text-green-800 border-green-300 dark:bg-green-900 dark:text-green-200';
    if (confidence >= 0.65) return 'bg-yellow-100 text-yellow-800 border-yellow-300 dark:bg-yellow-900 dark:text-yellow-200';
    return 'bg-red-100 text-red-800 border-red-300 dark:bg-red-900 dark:text-red-200';
  };

  const getConfidenceIcon = (confidence: number) => {
    if (confidence >= 0.8) return <CheckCircle2 className="h-5 w-5" />;
    if (confidence >= 0.65) return <AlertCircle className="h-5 w-5" />;
    return <XCircle className="h-5 w-5" />;
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <div className="flex items-start justify-between">
          <CardTitle className="text-xl">Answer</CardTitle>
          <div className="flex items-center gap-2">
            <Badge
              variant="outline"
              className={cn(getConfidenceColor(response.confidence))}
            >
              {getConfidenceIcon(response.confidence)}
              <span className="ml-1">{(response.confidence * 100).toFixed(0)}%</span>
            </Badge>
            <Badge variant="outline" className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              {response.response_time_ms.toFixed(0)}ms
            </Badge>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {response.blocked ? (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertTitle>Query Blocked</AlertTitle>
            <AlertDescription>
              {response.answer || 'We couldn\'t find sufficient information to answer your question. Please try rephrasing or ask about a different topic.'}
            </AlertDescription>
          </Alert>
        ) : (
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <p className="text-foreground leading-relaxed whitespace-pre-wrap">
              {response.answer}
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};

