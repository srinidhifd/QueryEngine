/**
 * API Client Service for QueryEngine Backend with timeout & retry logic
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const REQUEST_TIMEOUT_MS = 60000; // 60 seconds
const MAX_RETRIES = 2;
const RETRY_DELAY_MS = 1000; // 1 second, exponential backoff

class ApiClient {
  private async requestWithRetry(
    endpoint: string,
    options: RequestInit = {},
    retryCount = 0
  ): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);

      // Retry on timeout or network errors
      if (
        (error instanceof TypeError && error.name === 'AbortError') ||
        (error instanceof TypeError && error.message.includes('Failed to fetch'))
      ) {
        if (retryCount < MAX_RETRIES) {
          const delay = RETRY_DELAY_MS * Math.pow(2, retryCount); // Exponential backoff
          await new Promise((resolve) => setTimeout(resolve, delay));
          return this.requestWithRetry(endpoint, options, retryCount + 1);
        }
        throw new Error('Request timeout: could not reach server after 2 retries. Please check your connection and try again.');
      }
      throw error;
    }
  }

  async request(endpoint: string, options: RequestInit = {}) {
    const defaultOptions = {
      headers: {
        'Content-Type': 'application/json',
      },
    };

    try {
      const response = await this.requestWithRetry(endpoint, {
        ...defaultOptions,
        ...options,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.error || `API Error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error && error.message.includes('Request timeout')) {
        console.error('Request timeout after retries');
        throw new Error('Request timeout. Server is not responding. Please try again.');
      }
      console.error('API Error:', error);
      throw error;
    }
  }

  // Status & Health Checks
  async getStatus() {
    return this.request('/api/status');
  }

  async getHealth() {
    return this.request('/api/health');
  }

  // SQL Generation
  async generateSQL(query: string) {
    return this.request('/api/sql/generate', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  // SQL Execution
  async executeSql(sqlQuery: string) {
    return this.request('/api/sql/execute', {
      method: 'POST',
      body: JSON.stringify({ sql_query: sqlQuery }),
    });
  }

  // Test Generation
  async generateTests(sqlQuery: string, userRequest: string) {
    return this.request('/api/tests/generate', {
      method: 'POST',
      body: JSON.stringify({
        sql_query: sqlQuery,
        user_request: userRequest,
      }),
    });
  }

  // Full Pipeline
  async runFullPipeline(query: string) {
    return this.request('/api/full-pipeline', {
      method: 'POST',
      body: JSON.stringify({ query }),
    });
  }

  // History
  async getHistory() {
    return this.request('/api/history');
  }

  // Agent Operations
  async refineSql(initialQuery: string, generatedSql: string, feedback: string) {
    return this.request('/api/agent/refine-sql', {
      method: 'POST',
      body: JSON.stringify({
        initial_query: initialQuery,
        generated_sql: generatedSql,
        validation_feedback: feedback,
      }),
    });
  }

  async validateTests(sqlQuery: string, testCode: string, testOutput: string) {
    return this.request('/api/agent/validate-tests', {
      method: 'POST',
      body: JSON.stringify({
        sql_query: sqlQuery,
        test_code: testCode,
        test_output: testOutput,
      }),
    });
  }

  async optimizeQuery(sqlQuery: string, metrics: object) {
    return this.request('/api/agent/optimize-query', {
      method: 'POST',
      body: JSON.stringify({
        sql_query: sqlQuery,
        performance_metrics: metrics,
      }),
    });
  }
}

export default new ApiClient();
