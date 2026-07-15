import { useEffect, useState } from 'react'
import { useNavigate, useLocation } from 'react-router-dom'
import { Copy, Check, ArrowLeft, Database, Zap } from 'lucide-react'

interface LocationState {
  query: string
  database: string
}

interface ResultData {
  status: string
  query: string
  final_status: string
  phases: {
    phase1: {
      status: string
      sql_query?: string
      error?: string
    }
    phase2: {
      status: string
      rows_returned?: number
      columns?: string[]
      sample_data?: Record<string, any>[]
    }
    phase3: {
      status: string
      test_code?: string
      test_output?: string
      exit_code?: number
      error?: string
    }
  }
  timestamp: string
}

// Mock data for all databases
const MOCK_DATA: { [key: string]: ResultData } = {
  sqlite: {
    status: 'success',
    query: 'Show total revenue by region',
    final_status: 'All phases completed successfully',
    phases: {
      phase1: {
        status: 'success',
        sql_query: `SELECT
  c.region,
  COUNT(o.order_id) as total_orders,
  SUM(o.total_amount) as total_revenue,
  AVG(o.total_amount) as avg_order_value
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.region
ORDER BY total_revenue DESC;`
      },
      phase2: {
        status: 'success',
        rows_returned: 8,
        columns: ['region', 'total_orders', 'total_revenue', 'avg_order_value'],
        sample_data: [
          { region: 'North America', total_orders: 42, total_revenue: 125000.50, avg_order_value: 2976.20 },
          { region: 'Europe', total_orders: 38, total_revenue: 98500.75, avg_order_value: 2592.65 },
          { region: 'Asia Pacific', total_orders: 35, total_revenue: 87200.25, avg_order_value: 2491.44 },
          { region: 'Latin America', total_orders: 28, total_revenue: 65300.00, avg_order_value: 2332.14 }
        ]
      },
      phase3: {
        status: 'success',
        exit_code: 0,
        test_code: `import pytest

def test_sql_aggregation():
    """Verify SQL aggregation functions work"""
    assert 'SUM' in query or 'AVG' in query

def test_group_by_clause():
    """Verify GROUP BY is present"""
    assert 'GROUP BY' in query

def test_column_selection():
    """Verify all required columns selected"""
    assert 'region' in query.lower()`,
        test_output: `===== 3 passed in 0.04s =====\nAll tests passed successfully!`
      }
    },
    timestamp: new Date().toISOString()
  },
  postgresql: {
    status: 'success',
    query: 'Show total revenue by region',
    final_status: 'All phases completed successfully',
    phases: {
      phase1: {
        status: 'success',
        sql_query: `SELECT
  c.region,
  COUNT(o.order_id) as total_orders,
  SUM(o.total_amount) as total_revenue,
  AVG(o.total_amount) as avg_order_value,
  PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY o.total_amount) as median_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.region
ORDER BY total_revenue DESC;`
      },
      phase2: {
        status: 'success',
        rows_returned: 8,
        columns: ['region', 'total_orders', 'total_revenue', 'avg_order_value', 'median_order'],
        sample_data: [
          { region: 'North America', total_orders: 42, total_revenue: 125000.50, avg_order_value: 2976.20, median_order: 2800.00 },
          { region: 'Europe', total_orders: 38, total_revenue: 98500.75, avg_order_value: 2592.65, median_order: 2450.00 }
        ]
      },
      phase3: {
        status: 'success',
        exit_code: 0,
        test_code: `def test_percentile_function():
    assert 'PERCENTILE_CONT' in query

def test_window_function():
    assert 'WITHIN GROUP' in query`,
        test_output: `===== 2 passed in 0.03s =====`
      }
    },
    timestamp: new Date().toISOString()
  },
  mysql: {
    status: 'success',
    query: 'List top 5 customers by order count',
    final_status: 'All phases completed successfully',
    phases: {
      phase1: {
        status: 'success',
        sql_query: `SELECT
  c.customer_id,
  c.name,
  c.segment,
  COUNT(o.order_id) as order_count,
  SUM(o.total_amount) as total_spent,
  MAX(o.order_date) as last_order_date
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.segment
ORDER BY order_count DESC
LIMIT 5;`
      },
      phase2: {
        status: 'success',
        rows_returned: 5,
        columns: ['customer_id', 'name', 'segment', 'order_count', 'total_spent', 'last_order_date'],
        sample_data: [
          { customer_id: 1, name: 'ACME Corp', segment: 'Enterprise', order_count: 18, total_spent: 45000.00, last_order_date: '2024-07-10' },
          { customer_id: 5, name: 'TechStart Inc', segment: 'Startup', order_count: 12, total_spent: 28500.50, last_order_date: '2024-07-08' }
        ]
      },
      phase3: {
        status: 'success',
        exit_code: 0,
        test_code: `def test_limit_clause():
    assert 'LIMIT 5' in query

def test_order_by():
    assert 'ORDER BY' in query`,
        test_output: `===== 2 passed in 0.02s =====`
      }
    },
    timestamp: new Date().toISOString()
  },
  'aws-rds': {
    status: 'success',
    query: 'Find customers with more than 5 orders',
    final_status: 'All phases completed successfully',
    phases: {
      phase1: {
        status: 'success',
        sql_query: `SELECT
  c.customer_id,
  c.name,
  c.country,
  COUNT(o.order_id) as order_count,
  SUM(o.total_amount) as lifetime_value
FROM customers c
INNER JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.name, c.country
HAVING COUNT(o.order_id) > 5
ORDER BY order_count DESC;`
      },
      phase2: {
        status: 'success',
        rows_returned: 12,
        columns: ['customer_id', 'name', 'country', 'order_count', 'lifetime_value'],
        sample_data: [
          { customer_id: 2, name: 'Global Trading Ltd', country: 'United Kingdom', order_count: 16, lifetime_value: 52300.00 },
          { customer_id: 8, name: 'Innovation Labs', country: 'Canada', order_count: 14, lifetime_value: 48700.25 }
        ]
      },
      phase3: {
        status: 'success',
        exit_code: 0,
        test_code: `def test_having_clause():
    assert 'HAVING COUNT' in query

def test_inner_join():
    assert 'INNER JOIN' in query`,
        test_output: `===== 2 passed in 0.02s =====`
      }
    },
    timestamp: new Date().toISOString()
  },
  azure: {
    status: 'success',
    query: 'Calculate average order value by customer segment',
    final_status: 'All phases completed successfully',
    phases: {
      phase1: {
        status: 'success',
        sql_query: `SELECT
  c.segment,
  COUNT(DISTINCT c.customer_id) as customer_count,
  COUNT(o.order_id) as total_orders,
  AVG(o.total_amount) as avg_order_value,
  MIN(o.total_amount) as min_order,
  MAX(o.total_amount) as max_order
FROM customers c
LEFT JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.segment
ORDER BY avg_order_value DESC;`
      },
      phase2: {
        status: 'success',
        rows_returned: 4,
        columns: ['segment', 'customer_count', 'total_orders', 'avg_order_value', 'min_order', 'max_order'],
        sample_data: [
          { segment: 'Enterprise', customer_count: 8, total_orders: 65, avg_order_value: 3150.75, min_order: 1500.00, max_order: 5000.00 },
          { segment: 'Mid-Market', customer_count: 12, total_orders: 48, avg_order_value: 2450.50, min_order: 800.00, max_order: 4200.00 }
        ]
      },
      phase3: {
        status: 'success',
        exit_code: 0,
        test_code: `def test_min_max_functions():
    assert 'MIN' in query and 'MAX' in query

def test_distinct_count():
    assert 'COUNT(DISTINCT' in query`,
        test_output: `===== 2 passed in 0.02s =====`
      }
    },
    timestamp: new Date().toISOString()
  },
  oracle: {
    status: 'success',
    query: 'Show monthly sales trends',
    final_status: 'All phases completed successfully',
    phases: {
      phase1: {
        status: 'success',
        sql_query: `SELECT
  TRUNC(o.order_date, 'MONTH') as month,
  COUNT(o.order_id) as orders_count,
  SUM(o.total_amount) as monthly_revenue,
  AVG(o.total_amount) as avg_order_value,
  COUNT(DISTINCT o.customer_id) as unique_customers
FROM orders o
GROUP BY TRUNC(o.order_date, 'MONTH')
ORDER BY month DESC;`
      },
      phase2: {
        status: 'success',
        rows_returned: 12,
        columns: ['month', 'orders_count', 'monthly_revenue', 'avg_order_value', 'unique_customers'],
        sample_data: [
          { month: '2024-07-01', orders_count: 18, monthly_revenue: 54000.00, avg_order_value: 3000.00, unique_customers: 14 },
          { month: '2024-06-01', orders_count: 15, monthly_revenue: 42500.50, avg_order_value: 2833.37, unique_customers: 12 }
        ]
      },
      phase3: {
        status: 'success',
        exit_code: 0,
        test_code: `def test_trunc_function():
    assert 'TRUNC' in query

def test_monthly_grouping():
    assert 'MONTH' in query`,
        test_output: `===== 2 passed in 0.02s =====`
      }
    },
    timestamp: new Date().toISOString()
  }
}

const SkeletonLoader = ({ lines = 3, height = 'h-4' }: { lines?: number; height?: string }) => (
  <div className="space-y-3">
    {Array.from({ length: lines }).map((_, i) => (
      <div key={i} className={`${height} bg-white/10 rounded-lg animate-pulse`} />
    ))}
  </div>
)

export const ResultsPage = () => {
  const navigate = useNavigate()
  const location = useLocation()
  const state = location.state as LocationState

  const [result, setResult] = useState<ResultData | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!state?.query) {
      navigate('/')
      return
    }

    const runQuery = async () => {
      try {
        setLoading(true)
        setError(null)

        // Use mock data based on selected database
        const mockData = MOCK_DATA[state.database] || MOCK_DATA['sqlite']

        // Simulate loading delay
        await new Promise(resolve => setTimeout(resolve, 1500))

        setResult(mockData)
      } catch (err) {
        setError(
          err instanceof Error ? err.message : 'Failed to fetch results'
        )
      } finally {
        setLoading(false)
      }
    }

    runQuery()
  }, [state, navigate])

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (!state?.query) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-midnight-black via-slate-900 to-midnight-black flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-white mb-4">No Query Found</h1>
          <p className="text-gray-400 mb-6">Please go back and select a query to view results.</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-primary-teal text-black font-bold rounded-lg hover:bg-opacity-90 transition-all"
          >
            Back to Home
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-midnight-black via-slate-900 to-midnight-black">
      {/* Header */}
      <header className="bg-gradient-to-r from-midnight-black via-midnight-black/95 to-slate-900 backdrop-blur-md border-b border-primary-teal/30 sticky top-0 z-50 shadow-lg">
        <div className="max-w-7xl mx-auto px-6 py-4">
          {/* Top Row: Back Button & Title */}
          <div className="flex items-center justify-between gap-4 mb-4">
            <button
              onClick={() => navigate('/')}
              className="flex items-center gap-2 text-primary-teal hover:text-cyan-300 font-semibold transition-colors text-sm hover:gap-3 duration-200"
            >
              <ArrowLeft className="w-5 h-5 flex-shrink-0" />
              <span>Back</span>
            </button>
            <h1 className="text-2xl font-bold text-white">Results</h1>
            <div className="w-20" />
          </div>

          {/* Bottom Row: Database & Query Info */}
          <div className="grid grid-cols-3 gap-6 items-start">
            {/* Database */}
            <div className="flex items-center gap-3">
              <div className="flex-shrink-0">
                <Database className="w-5 h-5 text-primary-teal/70" />
              </div>
              <div className="min-w-0">
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Database</p>
                <p className="text-sm font-bold text-primary-teal capitalize">{state.database}</p>
              </div>
            </div>

            {/* Your Query */}
            <div className="col-span-2">
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-1">Your Query</p>
              <p className="text-sm text-gray-200 font-medium break-words line-clamp-2 hover:line-clamp-none transition-all" title={state.query}>
                {state.query}
              </p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-6 py-12">
        {loading && (
          <div className="space-y-8">
            {/* Phase 1 Skeleton */}
            <div className="bg-gradient-to-br from-card-dark to-slate-800/50 rounded-2xl border border-primary-teal/20 p-8 shadow-xl">
              <h2 className="text-xl font-bold text-white mb-6">Phase 1: SQL Generation</h2>
              <SkeletonLoader lines={5} height="h-6" />
            </div>

            {/* Phase 2 Skeleton */}
            <div className="bg-gradient-to-br from-card-dark to-slate-800/50 rounded-2xl border border-primary-teal/20 p-8 shadow-xl">
              <h2 className="text-xl font-bold text-white mb-6">Phase 2: Query Execution</h2>
              <SkeletonLoader lines={8} height="h-4" />
            </div>

            {/* Phase 3 Skeleton */}
            <div className="bg-gradient-to-br from-card-dark to-slate-800/50 rounded-2xl border border-primary-teal/20 p-8 shadow-xl">
              <h2 className="text-xl font-bold text-white mb-6">Phase 3: Test Results</h2>
              <SkeletonLoader lines={6} height="h-4" />
            </div>

            {/* Summary Skeleton */}
            <div className="bg-gradient-to-br from-card-dark to-slate-800/50 rounded-2xl border border-primary-teal/20 p-8 shadow-xl">
              <h2 className="text-xl font-bold text-white mb-6">Results Summary</h2>
              <div className="grid grid-cols-3 gap-4">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="bg-midnight-black/40 rounded-xl p-4 border border-primary-teal/20">
                    <SkeletonLoader lines={3} height="h-4" />
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {error && (
          <div className="bg-red-900/30 border border-red-500/50 rounded-2xl p-8 mb-6">
            <h3 className="text-red-300 font-bold mb-2 text-lg">Error</h3>
            <p className="text-red-200">{error}</p>
          </div>
        )}

        {result && !loading && (
          <div className="space-y-8">
            {/* Phase 1: SQL Generation */}
            <div className="bg-gradient-to-br from-card-dark to-slate-800/50 rounded-2xl border border-primary-teal/20 p-8 shadow-xl">
              <div className="flex items-center gap-3 mb-6">
                <Zap className="w-6 h-6 text-primary-teal" />
                <h2 className="text-2xl font-bold text-white">Phase 1: SQL Generation</h2>
                <span className="ml-auto text-xs bg-green-900/30 text-green-300 px-3 py-1 rounded-lg border border-green-500/30">✓ Complete</span>
              </div>
              {result?.phases?.phase1?.sql_query ? (
                <>
                  <div className="relative mb-6">
                    <button
                      onClick={() => copyToClipboard(result.phases.phase1.sql_query!)}
                      className="absolute top-3 right-3 p-2 bg-primary-teal/20 hover:bg-primary-teal/40 rounded-lg transition-colors text-primary-teal"
                    >
                      {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    </button>
                    <pre className="bg-slate-900/80 border border-primary-teal/30 text-gray-100 p-6 rounded-xl overflow-auto max-h-96 text-sm font-mono">
                      <code>{result.phases.phase1.sql_query}</code>
                    </pre>
                  </div>
                  <div className="flex items-center gap-2 text-green-400">
                    <Check className="w-5 h-5" />
                    <span className="font-semibold">Valid SQL</span>
                  </div>
                </>
              ) : (
                <div className="text-red-400 text-lg">{result?.phases?.phase1?.error || 'No SQL generated'}</div>
              )}
            </div>

            {/* Phase 2: Query Execution */}
            <div className="bg-gradient-to-br from-card-dark to-slate-800/50 rounded-2xl border border-primary-teal/20 p-8 shadow-xl">
              <div className="flex items-center gap-3 mb-6">
                <Database className="w-6 h-6 text-blue-400" />
                <h2 className="text-2xl font-bold text-white">Phase 2: Query Execution</h2>
                <span className="ml-auto text-xs bg-blue-900/30 text-blue-300 px-3 py-1 rounded-lg border border-blue-500/30">✓ Complete</span>
              </div>
              <div className="grid grid-cols-3 gap-4 mb-8">
                <div className="bg-midnight-black/40 rounded-xl p-4 border border-primary-teal/20">
                  <p className="text-gray-400 text-sm mb-1">Rows Returned</p>
                  <p className="text-2xl font-bold text-primary-teal">{result?.phases?.phase2?.rows_returned || 0}</p>
                </div>
                <div className="bg-midnight-black/40 rounded-xl p-4 border border-primary-teal/20">
                  <p className="text-gray-400 text-sm mb-1">Columns</p>
                  <p className="text-2xl font-bold text-cyan-400">{result?.phases?.phase2?.columns?.length || 0}</p>
                </div>
                <div className="bg-midnight-black/40 rounded-xl p-4 border border-primary-teal/20">
                  <p className="text-gray-400 text-sm mb-1">Status</p>
                  <p className="text-2xl font-bold text-green-400">✓ Success</p>
                </div>
              </div>

              {result?.phases?.phase2?.sample_data && result.phases.phase2.sample_data.length > 0 ? (
                <div className="overflow-x-auto border border-primary-teal/20 rounded-xl">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="bg-midnight-black/60 border-b border-primary-teal/20">
                        {result.phases.phase2.columns?.map((col) => (
                          <th key={col} className="px-4 py-3 text-left text-primary-teal font-semibold">
                            {col}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {result.phases.phase2.sample_data.map((row: any, idx: number) => (
                        <tr key={idx} className="border-b border-primary-teal/10 hover:bg-midnight-black/40 transition-colors">
                          {result.phases.phase2.columns?.map((col) => (
                            <td key={`${idx}-${col}`} className="px-4 py-3 text-gray-300">
                              {JSON.stringify(row[col])}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-gray-400 text-center py-8">No data returned</div>
              )}
            </div>

            {/* Phase 3: Test Execution */}
            <div className="bg-gradient-to-br from-card-dark to-slate-800/50 rounded-2xl border border-primary-teal/20 p-8 shadow-xl">
              <div className="flex items-center gap-3 mb-6">
                <Check className={`w-6 h-6 ${(result?.phases?.phase3?.exit_code ?? 1) === 0 ? 'text-green-400' : 'text-red-400'}`} />
                <h2 className="text-2xl font-bold text-white">Phase 3: Test Execution</h2>
                <span className={`ml-auto text-xs px-3 py-1 rounded-lg border ${(result?.phases?.phase3?.exit_code ?? 1) === 0 ? 'bg-green-900/30 text-green-300 border-green-500/30' : 'bg-red-900/30 text-red-300 border-red-500/30'}`}>
                  {(result?.phases?.phase3?.exit_code ?? 1) === 0 ? '✓ Passed' : '✗ Failed'}
                </span>
              </div>

              <div className="mb-8">
                <h3 className="text-lg font-semibold text-white mb-4">Test Code</h3>
                {result?.phases?.phase3?.test_code ? (
                  <div className="relative mb-4">
                    <button
                      onClick={() => copyToClipboard(result.phases.phase3.test_code!)}
                      className="absolute top-3 right-3 p-2 bg-primary-teal/20 hover:bg-primary-teal/40 rounded-lg transition-colors text-primary-teal"
                    >
                      {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                    </button>
                    <pre className="bg-slate-900/80 border border-primary-teal/30 text-gray-100 p-6 rounded-xl overflow-auto max-h-64 text-sm font-mono">
                      <code>{result.phases.phase3.test_code}</code>
                    </pre>
                  </div>
                ) : (
                  <p className="text-gray-400">No test code generated</p>
                )}
              </div>

              <div>
                <h3 className="text-lg font-semibold text-white mb-4">Execution Output</h3>
                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="bg-midnight-black/40 rounded-xl p-4 border border-primary-teal/20">
                    <p className="text-gray-400 text-sm mb-1">Exit Code</p>
                    <p className={`text-2xl font-bold ${(result?.phases?.phase3?.exit_code ?? 1) === 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {(result?.phases?.phase3?.exit_code ?? 1) === 0 ? '✓ 0' : `✗ ${result?.phases?.phase3?.exit_code}`}
                    </p>
                  </div>
                  <div className="bg-midnight-black/40 rounded-xl p-4 border border-primary-teal/20">
                    <p className="text-gray-400 text-sm mb-1">Status</p>
                    <p className={`text-2xl font-bold ${(result?.phases?.phase3?.exit_code ?? 1) === 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {(result?.phases?.phase3?.exit_code ?? 1) === 0 ? 'Passed' : 'Failed'}
                    </p>
                  </div>
                </div>

                <div className="bg-slate-900/80 border border-primary-teal/30 text-gray-100 p-6 rounded-xl overflow-auto max-h-64 text-sm font-mono whitespace-pre-wrap break-words">
                  {result?.phases?.phase3?.test_output || 'No output'}
                </div>
                {result?.phases?.phase3?.error && (
                  <p className="text-red-400 mt-4">{result.phases.phase3.error}</p>
                )}
              </div>
            </div>

            {/* Summary */}
            {result && (
              <div className="mt-12 bg-gradient-to-br from-card-dark to-slate-800/50 rounded-2xl border border-primary-teal/20 p-8 shadow-xl">
                <h2 className="text-2xl font-bold text-white mb-8">Execution Summary</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-gradient-to-br from-green-900/40 to-green-900/20 rounded-xl p-6 border border-green-500/30">
                    <div className="flex items-center gap-3 mb-3">
                      <Check className="w-6 h-6 text-green-400" />
                      <p className="text-gray-300 font-semibold">Phase 1</p>
                    </div>
                    <p className="text-gray-400 text-sm">SQL Generated</p>
                    <p className="text-lg font-bold text-green-400 mt-2">✓ Complete</p>
                  </div>

                  <div className="bg-gradient-to-br from-blue-900/40 to-blue-900/20 rounded-xl p-6 border border-blue-500/30">
                    <div className="flex items-center gap-3 mb-3">
                      <Check className="w-6 h-6 text-blue-400" />
                      <p className="text-gray-300 font-semibold">Phase 2</p>
                    </div>
                    <p className="text-gray-400 text-sm">{result?.phases?.phase2?.rows_returned || 0} Rows Returned</p>
                    <p className="text-lg font-bold text-blue-400 mt-2">✓ Success</p>
                  </div>

                  <div className={`bg-gradient-to-br ${(result?.phases?.phase3?.exit_code ?? 1) === 0 ? 'from-green-900/40 to-green-900/20' : 'from-red-900/40 to-red-900/20'} rounded-xl p-6 border ${(result?.phases?.phase3?.exit_code ?? 1) === 0 ? 'border-green-500/30' : 'border-red-500/30'}`}>
                    <div className="flex items-center gap-3 mb-3">
                      <Check className={`w-6 h-6 ${(result?.phases?.phase3?.exit_code ?? 1) === 0 ? 'text-green-400' : 'text-red-400'}`} />
                      <p className="text-gray-300 font-semibold">Phase 3</p>
                    </div>
                    <p className="text-gray-400 text-sm">Tests {(result?.phases?.phase3?.exit_code ?? 1) === 0 ? 'Passed' : 'Failed'}</p>
                    <p className={`text-lg font-bold mt-2 ${(result?.phases?.phase3?.exit_code ?? 1) === 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {(result?.phases?.phase3?.exit_code ?? 1) === 0 ? '✓ Passed' : '✗ Failed'}
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
