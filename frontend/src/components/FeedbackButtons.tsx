import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, CheckCircle2 } from 'lucide-react';
import { Button } from './ui/button';
import { cn } from '../lib/utils';

interface FeedbackButtonsProps {
  queryId?: number;
  onFeedback: (queryId: number, feedback: 'positive' | 'negative') => Promise<void>;
  disabled?: boolean;
}

export const FeedbackButtons: React.FC<FeedbackButtonsProps> = ({
  queryId,
  onFeedback,
  disabled = false,
}) => {
  const [feedbackGiven, setFeedbackGiven] = useState<'positive' | 'negative' | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [showThankYou, setShowThankYou] = useState(false);

  if (!queryId) {
    return null;
  }

  const handleFeedback = async (feedback: 'positive' | 'negative') => {
    if (feedbackGiven || submitting || disabled) return;

    setSubmitting(true);
    try {
      await onFeedback(queryId, feedback);
      setFeedbackGiven(feedback);
      setShowThankYou(true);
      setTimeout(() => setShowThankYou(false), 3000);
    } catch (error) {
      console.error('Failed to submit feedback:', error);
      // You could show an error toast here
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-muted-foreground">Was this helpful?</span>
      <div className="flex items-center gap-2">
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleFeedback('positive')}
          disabled={feedbackGiven !== null || submitting || disabled}
          className={cn(
            'gap-2',
            feedbackGiven === 'positive' && 'bg-green-50 border-green-300 dark:bg-green-900/20'
          )}
        >
          <ThumbsUp className={cn('h-4 w-4', feedbackGiven === 'positive' && 'text-green-600')} />
          Yes
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => handleFeedback('negative')}
          disabled={feedbackGiven !== null || submitting || disabled}
          className={cn(
            'gap-2',
            feedbackGiven === 'negative' && 'bg-red-50 border-red-300 dark:bg-red-900/20'
          )}
        >
          <ThumbsDown className={cn('h-4 w-4', feedbackGiven === 'negative' && 'text-red-600')} />
          No
        </Button>
      </div>
      {showThankYou && (
        <div className="flex items-center gap-1 text-sm text-green-600 dark:text-green-400 animate-in fade-in">
          <CheckCircle2 className="h-4 w-4" />
          <span>Thank you!</span>
        </div>
      )}
    </div>
  );
};

