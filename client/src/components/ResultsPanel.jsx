import React, { useState, useMemo } from 'react'
import { ChevronUp, ChevronDown, Download, Eye, EyeOff } from 'lucide-react'

export default function ResultsPanel({ results }) {
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'asc' })
  const [hiddenColumns, setHiddenColumns] = useState(new Set())
  const [expandedRow, setExpandedRow] = useState(null)

  const headers = useMemo(() => 
    results && results.length > 0 ? Object.keys(results[0]) : [],
    [results]
  )
  
  const visibleHeaders = useMemo(() => 
    headers.filter(h => !hiddenColumns.has(h)),
    [headers, hiddenColumns]
  )

  const sortedResults = useMemo(() => {
    if (!sortConfig.key || !results || results.length === 0) return results || []
    const sorted = [...results].sort((a, b) => {
      const aVal = a[sortConfig.key]
      const bVal = b[sortConfig.key]
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortConfig.direction === 'asc' ? aVal - bVal : bVal - aVal
      }
      
      const aStr = String(aVal).toLowerCase()
      const bStr = String(bVal).toLowerCase()
      return sortConfig.direction === 'asc' 
        ? aStr.localeCompare(bStr)
        : bStr.localeCompare(aStr)
    })
    return sorted
  }, [results, sortConfig])

  const handleSort = (key) => {
    setSortConfig(prev => ({
      key,
      direction: prev.key === key && prev.direction === 'asc' ? 'desc' : 'asc'
    }))
  }

  const toggleColumnVisibility = (col) => {
    const newHidden = new Set(hiddenColumns)
    if (newHidden.has(col)) {
      newHidden.delete(col)
    } else {
      newHidden.add(col)
    }
    setHiddenColumns(newHidden)
  }

  const exportToCSV = () => {
    const csv = [
      visibleHeaders.join(','),
      ...sortedResults.map(row =>
        visibleHeaders.map(h => {
          const val = row[h]
          return typeof val === 'string' && val.includes(',') ? `"${val}"` : val
        }).join(',')
      )
    ].join('\n')
    
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `results-${new Date().toISOString().split('T')[0]}.csv`
    a.click()
  }

  return (
    <div className="bg-white border border-gray-300 rounded overflow-hidden">
      {!results || results.length === 0 ? (
        <div className="p-12 text-center">
          <div className="text-gray-600">
            <p className="mb-2 text-lg">📊 No Results</p>
            <p className="text-sm">Run a query to see student records here</p>
          </div>
        </div>
      ) : (
        <>
          {/* Header */}
          <div className="px-6 py-4 border-b border-gray-300 bg-gray-50 flex items-center justify-between">
            <div>
              <h3 className="text-lg font-semibold flex items-center gap-2 text-black">
                <div className="w-2 h-2 rounded-full bg-black"></div>
                Query Results
              </h3>
              <p className="text-xs text-gray-700 mt-1">{sortedResults.length} record{sortedResults.length !== 1 ? 's' : ''} found</p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={exportToCSV}
                className="p-2 rounded-lg hover:bg-gray-200 transition-smooth text-black hover:text-black"
                title="Export to CSV"
              >
                <Download size={18} />
              </button>
            </div>
          </div>

          {/* Column Visibility Toggle */}
          <div className="px-6 py-3 border-b border-gray-300 bg-gray-100 flex items-center gap-2 overflow-x-auto">
            <span className="text-xs text-gray-800 shrink-0 font-medium">Columns:</span>
            <div className="flex gap-2 overflow-x-auto pb-1">
              {headers.map(col => (
                <button
                  key={col}
                  onClick={() => toggleColumnVisibility(col)}
                  className={`text-xs px-2 py-1 rounded transition-smooth shrink-0 flex items-center gap-1 font-medium ${
                    hiddenColumns.has(col)
                      ? 'bg-gray-300 text-gray-800 hover:bg-gray-400'
                      : 'bg-black text-white hover:bg-gray-900'
                  }`}
                >
                  {hiddenColumns.has(col) ? (
                    <EyeOff size={12} />
                  ) : (
                    <Eye size={12} />
                  )}
                  {col.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-100 border-b border-gray-300">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-black w-12">#</th>
                  {visibleHeaders.map(h => (
                    <th
                      key={h}
                      onClick={() => handleSort(h)}
                      className="px-4 py-3 text-left text-xs font-semibold text-black cursor-pointer hover:bg-gray-200 transition-smooth"
                    >
                      <div className="flex items-center gap-1">
                        <span>{h.replace(/_/g, ' ')}</span>
                        {sortConfig.key === h && (
                          sortConfig.direction === 'asc' 
                            ? <ChevronUp size={14} className="text-black" />
                            : <ChevronDown size={14} className="text-black" />
                        )}
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {sortedResults.map((row, i) => (
                  <React.Fragment key={i}>
                    <tr className={`border-b border-gray-300 hover:bg-gray-100 transition-smooth cursor-pointer ${i % 2 === 0 ? 'bg-gray-50' : 'bg-white'}`}>
                      <td className="px-4 py-3 text-xs text-gray-600 font-mono">{i + 1}</td>
                      {visibleHeaders.map(h => (
                        <td key={`${i}-${h}`} className="px-4 py-3 text-black">
                          {typeof row[h] === 'boolean' ? (
                            <span className={`px-2 py-1 rounded text-xs font-medium ${
                              row[h] ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                            }`}>
                              {row[h] ? '✓ Yes' : '✗ No'}
                            </span>
                          ) : (
                            <span className="truncate max-w-xs block">{row[h]}</span>
                          )}
                        </td>
                      ))}
                    </tr>
                  </React.Fragment>
                ))}
              </tbody>
            </table>
          </div>

          {/* Footer */}
          <div className="px-6 py-3 border-t border-gray-300 bg-gray-50 text-xs text-gray-800 flex items-center justify-between">
            <span>Showing {sortedResults.length} of {sortedResults.length} results</span>
            <span className="font-medium">{visibleHeaders.length} of {headers.length} columns visible</span>
          </div>
        </>
      )}
    </div>
  )
}
