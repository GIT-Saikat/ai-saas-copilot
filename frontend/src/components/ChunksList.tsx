import React, { useState, useMemo } from 'react';
import { ChevronDown, ChevronUp, FileText, Tag, ExternalLink } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Button } from './ui/button';
import { cn } from '../lib/utils';
import { Chunk } from '../types';

interface ChunksListProps {
  chunks: Chunk[];
  query?: string; // Original query for keyword highlighting
}

export const ChunksList: React.FC<ChunksListProps> = ({ chunks, query = '' }) => {
  const [expandedChunks, setExpandedChunks] = useState<Set<number>>(new Set());

  // Extract keywords from query for highlighting
  const keywords = useMemo(() => {
    if (!query) return [];
    return query
      .toLowerCase()
      .split(/\s+/)
      .filter(word => word.length > 2) // Only highlight words longer than 2 chars
      .filter(word => !['the', 'and', 'or', 'but', 'for', 'with', 'from'].includes(word)); // Filter common words
  }, [query]);

  // Highlight keywords in text
  const highlightText = (text: string) => {
    if (!keywords.length) return text;
    
    const parts = text.split(new RegExp(`(${keywords.join('|')})`, 'gi'));
    return parts.map((part, index) => {
      const isKeyword = keywords.some(kw => part.toLowerCase() === kw.toLowerCase());
      return isKeyword ? (
        <mark key={index} className="bg-yellow-200 dark:bg-yellow-900/50 px-1 rounded">
          {part}
        </mark>
      ) : (
        part
      );
    });
  };

  // Check if source is a URL
  const isUrl = (str: string | undefined): boolean => {
    if (!str) return false;
    try {
      new URL(str);
      return true;
    } catch {
      return false;
    }
  };

  const toggleChunk = (index: number) => {
    const newExpanded = new Set(expandedChunks);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedChunks(newExpanded);
  };

  if (chunks.length === 0) {
    return null;
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'bg-green-500';
    if (score >= 0.65) return 'bg-yellow-500';
    return 'bg-red-500';
  };

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="text-xl flex items-center gap-2">
          <FileText className="h-5 w-5" />
          Retrieved Sources ({chunks.length})
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {chunks.map((chunk, index) => {
          const isExpanded = expandedChunks.has(index);
          const scorePercentage = (chunk.score * 100).toFixed(0);

          return (
            <div
              key={index}
              className="border rounded-lg p-4 space-y-3 hover:bg-accent/50 transition-colors"
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1 space-y-2">
                  <div className="flex items-center gap-2 flex-wrap">
                    <Badge variant="secondary" className="flex items-center gap-1">
                      <Tag className="h-3 w-3" />
                      {chunk.metadata.category}
                    </Badge>
                    <Badge variant="outline" className="text-xs">
                      ID: {chunk.metadata.id}
                    </Badge>
                    <div className="flex items-center gap-2">
                      <div className="h-2 w-16 bg-muted rounded-full overflow-hidden">
                        <div
                          className={cn(
                            'h-full transition-all',
                            getScoreColor(chunk.score)
                          )}
                          style={{ width: `${chunk.score * 100}%` }}
                        />
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {scorePercentage}%
                      </span>
                    </div>
                  </div>
                </div>
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={() => toggleChunk(index)}
                  className="h-8 w-8"
                >
                  {isExpanded ? (
                    <ChevronUp className="h-4 w-4" />
                  ) : (
                    <ChevronDown className="h-4 w-4" />
                  )}
                </Button>
              </div>

              {isExpanded && (
                <div className="pt-2 border-t">
                  <p className="text-sm text-foreground leading-relaxed whitespace-pre-wrap">
                    {highlightText(chunk.content)}
                  </p>
                  {chunk.metadata.source && (
                    <div className="mt-3 flex items-center gap-2">
                      <span className="text-xs text-muted-foreground">Source:</span>
                      {isUrl(chunk.metadata.source) ? (
                        <a
                          href={chunk.metadata.source}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-primary hover:underline flex items-center gap-1"
                        >
                          {chunk.metadata.source}
                          <ExternalLink className="h-3 w-3" />
                        </a>
                      ) : (
                        <span className="text-xs text-muted-foreground">
                          {chunk.metadata.source}
                        </span>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </CardContent>
    </Card>
  );
};

