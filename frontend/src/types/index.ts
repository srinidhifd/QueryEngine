// API Request/Response Types

export interface QueryRequest {
  query: string;
}

export interface SQLGenerationResponse {
  status: string;
  sql_query?: string;
  original_request?: string;
  is_valid: boolean;
  error?: string;
  tokens_used: number;
  timestamp: string;
}

export interface ExecutionResult {
  timestamp: string;
  status: string;
  rows_returned: number;
  columns: string[];
  sample_data: Record<string, any>[];
}

export interface TestGenerationResponse {
  status: string;
  test_code?: string;
  test_file?: string;
  error?: string;
  tokens_used: number;
  timestamp: string;
}

export interface FullPipelineResponse {
  status: string;
  query: string;
  final_status?: string;
  phases: {
    phase1?: {
      status: string;
      sql_query?: string;
      timestamp?: string;
      tokens_used?: number;
      error?: string;
    };
    execution?: {
      status: string;
      rows_returned?: number;
      columns?: string[];
      sample_data?: Record<string, any>[];
      timestamp?: string;
    };
    phase2?: {
      status: string;
      test_code?: string;
      test_file?: string;
      tests_passed?: boolean;
      timestamp?: string;
      tokens_used?: number;
      error?: string;
    };
  };
  timestamp: string;
}

// Agent Request/Response Types

export interface AgentRefineSqlRequest {
  initial_query: string;
  generated_sql: string;
  validation_feedback: string;
}

export interface AgentRefineSqlResponse {
  conversation_id: string;
  original_sql: string;
  refined_sql: string;
  reasoning: string;
  tokens_used: number;
  turns?: number;
}

export interface AgentValidateTestsRequest {
  sql_query: string;
  test_code: string;
  test_output: string;
}

export interface AgentValidateTestsResponse {
  conversation_id: string;
  original_tests: string;
  improved_tests: string;
  suggestions: string;
  tokens_used: number;
}

export interface AgentOptimizeQueryRequest {
  sql_query: string;
  performance_metrics?: Record<string, any>;
}

export interface AgentOptimizeQueryResponse {
  conversation_id: string;
  original_query: string;
  optimized_query: string;
  suggestions: string;
  tokens_used: number;
}

// UI Component Props

export interface QueryInputProps {
  onSubmit: (query: string) => void;
  isLoading: boolean;
}

export interface ResultsPanelProps {
  result: FullPipelineResponse | null;
  isLoading: boolean;
  onRefine?: (sql: string) => void;
  onOptimize?: (sql: string) => void;
}

export interface ErrorToastProps {
  message: string | null;
  onClose: () => void;
}

export interface LoadingModalProps {
  isOpen: boolean;
  phase: string;
}

// History Types

export interface QueryHistoryRecord {
  id: number;
  original_query: string;
  generated_sql?: string;
  execution_status: string;
  rows_returned?: number;
  cost_usd: number;
  created_at?: string;
}

export interface HistoryResponse {
  status: string;
  records: QueryHistoryRecord[];
}
