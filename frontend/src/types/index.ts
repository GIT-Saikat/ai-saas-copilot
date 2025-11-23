export interface ChunkMetadata {
  id: string;
  category: string;
  source?: string;
}

export interface Chunk {
  content: string;
  score: number;
  metadata: ChunkMetadata;
}

export interface QueryResponse {
  query: string;
  answer: string;
  chunks: Chunk[];
  blocked: boolean;
  confidence: number;
  response_time_ms: number;
  query_id?: number;
}

export interface FeedbackRequest {
  query_id: number;
  feedback: "positive" | "negative";
}

export interface AnalyticsResponse {
  total_queries: number;
  avg_confidence: number;
  blocked_queries: number;
  positive_feedback: number;
  negative_feedback: number;
  avg_response_time_ms: number;
  recent_queries: Array<{
    id: number;
    query: string;
    confidence: number;
    feedback?: string;
    created_at: string;
  }>;
}

export interface HealthResponse {
  status: string;
  version: string;
  timestamp?: string;
}

