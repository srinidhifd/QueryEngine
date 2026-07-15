import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Zap, Database } from 'lucide-react'

const DATABASES = [
  { value: 'sqlite', label: 'SQLite (Local)' },
  { value: 'postgresql', label: 'PostgreSQL' },
  { value: 'mysql', label: 'MySQL' },
  { value: 'aws-rds', label: 'AWS RDS' },
  { value: 'azure', label: 'Azure SQL' },
  { value: 'oracle', label: 'Oracle' },
]

const SAMPLE_QUERIES = [
  'Show total revenue by region',
  'List top 10 customers by spend',
  'Count active customers per country',
  'Find customers with highest average order value',
  'Show monthly sales trends for last 12 months',
  'List products ordered by sales volume',
  'Calculate customer lifetime value by segment',
  'Show repeat customer purchase frequency'
]

export const HomePage = () => {
  const navigate = useNavigate()
  const [query, setQuery] = useState('')
  const [selectedDatabase, setSelectedDatabase] = useState('sqlite')
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (!query.trim()) {
      setError('Please enter a query')
      return
    }
    setError(null)
    navigate('/results', {
      state: { query: query.trim(), database: selectedDatabase }
    })
  }

  const useSampleQuery = (sample: string) => {
    setQuery(sample)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-midnight-black via-slate-900 to-midnight-black flex flex-col">
      {/* Header */}
      <header className="bg-midnight-black/90 backdrop-blur-sm border-b border-primary-teal/20 sticky top-0 z-50 shadow-xl">
        <div className="max-w-7xl mx-auto px-6 py-6">
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 bg-gradient-to-br from-primary-teal to-cyan-400 rounded-xl flex items-center justify-center shadow-lg shadow-primary-teal/20">
              <Zap className="w-7 h-7 text-midnight-black font-bold" />
            </div>
            <div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-primary-teal to-cyan-400 bg-clip-text text-transparent">QueryEngine</h1>
              <p className="text-sm text-gray-400">Generate SQL from Natural Language + Auto Tests</p>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <div className="max-w-5xl mx-auto px-6 py-12">
          {/* Database Selector */}
          <div className="mb-10 bg-gradient-to-br from-card-dark to-slate-800/50 rounded-2xl border border-primary-teal/20 p-8 shadow-xl hover:shadow-2xl hover:shadow-primary-teal/10 transition-all">
            <div className="flex items-center gap-3 mb-4">
              <Database className="w-5 h-5 text-primary-teal" />
              <label className="block text-sm font-bold text-white font-heading">Select Database</label>
            </div>
            <select
              value={selectedDatabase}
              onChange={(e) => setSelectedDatabase(e.target.value)}
              className="w-full bg-midnight-black text-white border-2 border-primary-teal/30 rounded-xl px-4 py-3 focus:outline-none focus:border-primary-teal focus:ring-2 focus:ring-primary-teal/30 transition-all font-body hover:border-primary-teal/50"
            >
              {DATABASES.map((db) => (
                <option key={db.value} value={db.value}>
                  {db.label}
                </option>
              ))}
            </select>
            <p className="text-xs text-gray-400 mt-3 font-body">
              Query will execute against: <span className="text-primary-teal font-semibold">{DATABASES.find(d => d.value === selectedDatabase)?.label}</span>
            </p>
          </div>

          {/* Query Input */}
          <div className="bg-gradient-to-br from-card-dark to-slate-800/50 rounded-2xl border border-primary-teal/20 p-10 shadow-xl hover:shadow-2xl hover:shadow-primary-teal/10 transition-all mb-10">
            <h2 className="text-2xl font-bold text-white mb-6 font-heading">Your Query</h2>

            <form onSubmit={handleSubmit} className="space-y-6">
              <textarea
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                onKeyDown={(e) => {
                  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
                    handleSubmit(e as any)
                  }
                }}
                placeholder="Ask in plain English... (Ctrl/Cmd + Enter to submit)"
                rows={6}
                className="w-full px-5 py-4 border-2 border-primary-teal/30 bg-midnight-black rounded-xl focus:outline-none focus:border-primary-teal focus:ring-2 focus:ring-primary-teal/30 resize-none transition-all font-body text-white placeholder-gray-500 hover:border-primary-teal/50"
              />

              <button
                type="submit"
                disabled={!query.trim()}
                className="w-full bg-gradient-to-r from-primary-teal to-cyan-400 hover:shadow-lg hover:shadow-primary-teal/30 disabled:opacity-50 disabled:cursor-not-allowed text-midnight-black font-bold py-4 rounded-xl transition-all flex items-center justify-center gap-2 font-heading shadow-lg text-lg"
              >
                <Zap className="w-5 h-5" />
                Generate SQL & Tests (Ctrl+Enter)
              </button>
            </form>

            {error && (
              <div className="mt-4 p-4 bg-red-900/30 border border-red-500/50 rounded-lg text-red-300 text-sm font-body">
                {error}
              </div>
            )}
          </div>

          {/* Sample Queries */}
          <div className="bg-gradient-to-br from-card-dark to-slate-800/50 rounded-2xl border border-primary-teal/20 p-10 shadow-xl">
            <h3 className="text-xl font-bold text-white mb-6 font-heading">Sample Queries</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {SAMPLE_QUERIES.map((sample, idx) => (
                <button
                  key={idx}
                  onClick={() => useSampleQuery(sample)}
                  className="text-left p-4 bg-midnight-black/60 hover:bg-primary-teal/10 rounded-xl text-sm text-gray-300 transition-all border border-primary-teal/20 hover:border-primary-teal/60 group"
                >
                  <span className="text-primary-teal group-hover:text-cyan-400 transition-colors">→</span> {sample}
                </button>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
