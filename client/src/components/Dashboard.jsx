import React, { useMemo } from 'react'
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Legend, LineChart, Line, CartesianGrid } from 'recharts'
import { TrendingUp, Users, BarChart3, Filter } from 'lucide-react'

const COLORS = ['#000000', '#333333', '#666666', '#999999', '#cccccc']

export default function Dashboard({ results = [], condition = '' }) {
  // compute aggregates
  const byClass = useMemo(() => {
    const map = {}
    results.forEach(r => {
      const cls = r.class || 'Unknown'
      map[cls] = (map[cls] || 0) + 1
    })
    return Object.entries(map).map(([key, value]) => ({ name: key, value }))
  }, [results])

  const scores = useMemo(() => {
    if (!results.length) return []
    const map = {}
    results.forEach(r => {
      const cls = r.class || 'Unknown'
      map[cls] = map[cls] || { total: 0, count: 0 }
      map[cls].total += Number(r.quiz_score || 0)
      map[cls].count += 1
    })
    return Object.entries(map).map(([name, v]) => ({ name, avg: +(v.total / v.count).toFixed(1) }))
  }, [results])

  const stats = useMemo(() => {
    const total = results.length
    const avgScore = results.length > 0 
      ? (results.reduce((sum, r) => sum + (Number(r.quiz_score) || 0), 0) / results.length).toFixed(1)
      : 0
    return { total, avgScore }
  }, [results])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 bg-gray-200 rounded">
            <BarChart3 className="text-black" size={24} />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-black">Analytics Dashboard</h2>
            <p className="text-xs text-gray-600">Real-time insights from query results</p>
          </div>
        </div>
      </div>

      {/* Active Filter Display */}
      {condition && (
        <div className="p-4 bg-gray-50 border border-gray-300 rounded">
          <div className="flex items-start gap-3">
            <Filter size={18} className="text-black mt-0.5" />
            <div className="min-w-0">
              <p className="text-xs text-gray-600 mb-1">Active Filter Condition:</p>
              <p className="text-sm text-black font-mono bg-white p-2 rounded border border-gray-300 overflow-x-auto">
                {condition}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
        <div className="glass rounded-lg p-4 border border-gray-300 hover:border-gray-500 transition-smooth bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-700 font-medium">Total Results</p>
              <p className="text-2xl font-bold mt-1 text-black">{stats.total}</p>
            </div>
            <Users className="text-gray-700 opacity-40" size={24} />
          </div>
        </div>
        
        <div className="glass rounded-lg p-4 border border-gray-300 hover:border-gray-500 transition-smooth bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-700 font-medium">Avg Score</p>
              <p className="text-2xl font-bold mt-1 text-black">{stats.avgScore}</p>
            </div>
            <TrendingUp className="text-gray-700 opacity-40" size={24} />
          </div>
        </div>
        
        <div className="glass rounded-lg p-4 border border-gray-300 hover:border-gray-500 transition-smooth bg-white">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs text-gray-700 font-medium">Classes</p>
              <p className="text-2xl font-bold mt-1 text-black">{byClass.length}</p>
            </div>
            <BarChart3 className="text-gray-700 opacity-40" size={24} />
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Distribution Chart */}
        <div className="glass rounded-xl p-6 border border-gray-300 hover:border-gray-500 transition-smooth bg-white">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-black">
            <div className="w-2 h-2 rounded-full bg-black"></div>
            Distribution by Class
          </h3>
          {byClass.length ? (
            <ResponsiveContainer width="100%" height={240}>
              <PieChart>
                <Pie 
                  dataKey="value" 
                  data={byClass} 
                  cx="50%" 
                  cy="50%" 
                  outerRadius={80}
                  innerRadius={50}
                  paddingAngle={2}
                  label
                >
                  {byClass.map((entry, idx) => (
                    <Cell key={`cell-${idx}`} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    background: '#f5f5f5',
                    border: '1px solid #333',
                    borderRadius: '8px',
                    color: '#000'
                  }}
                  formatter={(value) => `${value} student${value !== 1 ? 's' : ''}`}
                />
              </PieChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-600">
              <p className="text-center">
                <Users className="mx-auto mb-2 opacity-50" size={32} />
                No data available
              </p>
            </div>
          )}
        </div>

        {/* Score Chart */}
        <div className="glass rounded-xl p-6 border border-gray-300 hover:border-gray-500 transition-smooth bg-white">
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2 text-black">
            <div className="w-2 h-2 rounded-full bg-black"></div>
            Average Quiz Score
          </h3>
          {scores.length ? (
            <ResponsiveContainer width="100%" height={240}>
              <BarChart 
                data={scores}
                margin={{ top: 20, right: 30, left: 0, bottom: 0 }}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="#ddd" />
                <XAxis dataKey="name" stroke="#666" />
                <YAxis domain={[0, 100]} stroke="#666" />
                <Tooltip 
                  contentStyle={{ 
                    background: '#f5f5f5',
                    border: '1px solid #333',
                    borderRadius: '8px',
                    color: '#000'
                  }}
                  formatter={(value) => `${value}/100`}
                />
                <Bar 
                  dataKey="avg" 
                  name="Avg Score" 
                  radius={[8, 8, 0, 0]}
                  animationDuration={800}
                >
                  {scores.map((_, idx) => (
                    <Cell key={`c-${idx}`} fill={COLORS[idx % COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-64 flex items-center justify-center text-gray-600">
              <p className="text-center">
                <TrendingUp className="mx-auto mb-2 opacity-50" size={32} />
                No scores yet
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Empty State */}
      {results.length === 0 && (
        <div className="glass rounded-xl p-12 border border-gray-300 text-center bg-white">
          <BarChart3 size={48} className="mx-auto mb-4 text-gray-600" />
          <h3 className="text-lg font-semibold text-gray-800 mb-2">No Results Yet</h3>
          <p className="text-sm text-gray-700">Run a query in the chat panel to see analytics here</p>
        </div>
      )}
    </div>
  )
}
