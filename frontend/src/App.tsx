import React, { useState, useCallback } from 'react';
import { SearchBar } from './components/SearchBar';
import { AnswerCard } from './components/AnswerCard';
import { ChunksList } from './components/ChunksList';
import { FeedbackButtons } from './components/FeedbackButtons';
import { AnalyticsDashboard } from './components/AnalyticsDashboard';
import { ConnectionStatus } from './components/ConnectionStatus';
import { Alert, AlertDescription, AlertTitle } from './components/ui/alert';
import { AlertCircle } from 'lucide-react';
import { Button } from './components/ui/button';
import { RefreshCw } from 'lucide-react';
import apiService from './services/api';
import { QueryResponse } from './types';
import './App.css';

function App() {
  const [response, setResponse] = useState<QueryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastQuery, setLastQuery] = useState<string | null>(null);

  const handleSearch = useCallback(async (searchQuery: string) => {
    setLoading(true);
    setError(null);
    setResponse(null);
    setLastQuery(searchQuery);

    try {
      const result = await apiService.query(searchQuery);
      setResponse(result);
    } catch (err: any) {
      setError(err.message || 'Failed to process query. Please try again.');
      console.error('Query error:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  const handleRetry = useCallback(() => {
    if (lastQuery) {
      handleSearch(lastQuery);
    }
  }, [lastQuery, handleSearch]);

  const handleFeedback = useCallback(async (queryId: number, feedback: 'positive' | 'negative') => {
    try {
      await apiService.submitFeedback(queryId, feedback);
    } catch (err: any) {
      console.error('Feedback error:', err);
      // Error is handled in FeedbackButtons component
      throw err;
    }
  }, []);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card sticky top-0 z-10 shadow-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl md:text-3xl font-bold text-foreground">
                SaaS Support Copilot
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                Ask questions and get answers from our documentation
              </p>
            </div>
            <ConnectionStatus />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto space-y-6">
          {/* Analytics Dashboard */}
          <AnalyticsDashboard />

          {/* Search Section */}
          <div className="space-y-4">
            <SearchBar onSearch={handleSearch} loading={loading} />
            
            {error && (
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertTitle>Error</AlertTitle>
                <AlertDescription className="flex items-center justify-between gap-4">
                  <span>{error}</span>
                  {(error.includes('Network error') || error.includes('timeout')) && lastQuery && (
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={handleRetry}
                      disabled={loading}
                      className="gap-2"
                    >
                      <RefreshCw className="h-4 w-4" />
                      Retry
                    </Button>
                  )}
                </AlertDescription>
              </Alert>
            )}
          </div>

          {/* Results Section */}
          {response && (
            <div className="space-y-6">
              <AnswerCard response={response} loading={loading} />
              
              {!response.blocked && (
                <>
                  <FeedbackButtons
                    queryId={response.query_id}
                    onFeedback={handleFeedback}
                    disabled={loading}
                  />
                  <ChunksList chunks={response.chunks} query={response.query} />
                </>
              )}
            </div>
          )}

          {/* Empty State */}
          {!response && !loading && !error && (
            <div className="text-center py-12 space-y-4">
              <div className="text-muted-foreground">
                <p className="text-lg mb-2">Welcome to the Support Copilot</p>
                <p className="text-sm">
                  Enter a question above to get started. Our AI will search through
                  our documentation to find the best answer for you.
                </p>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t mt-12 py-6">
        <div className="container mx-auto px-4 text-center text-sm text-muted-foreground">
          <p>Powered by RAG (Retrieval-Augmented Generation)</p>
        </div>
      </footer>
    </div>
  );
}

export default App;
