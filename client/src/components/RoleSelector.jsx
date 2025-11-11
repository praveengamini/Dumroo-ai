import React from 'react'
import { Shield, BookOpen, Layers } from 'lucide-react'

export default function RoleSelector({ role, setRole }) {
  const grades = [
    { value: null, label: 'All Grades', icon: '📊' },
    { value: 7, label: 'Grade 7', icon: '7️⃣' },
    { value: 8, label: 'Grade 8', icon: '8️⃣' },
    { value: 9, label: 'Grade 9', icon: '9️⃣' }
  ]
  
  const classes = [
    { value: null, label: 'All Classes', icon: '📚' },
    { value: 'A', label: 'Class A', icon: 'Ⓐ' },
    { value: 'B', label: 'Class B', icon: 'Ⓑ' },
    { value: 'C', label: 'Class C', icon: 'Ⓒ' }
  ]

  return (
    <div className="space-y-6 w-full">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-black rounded">
          <Shield className="text-white" size={24} />
        </div>
        <div>
          <h3 className="text-xl font-bold text-black">Access Control</h3>
          <p className="text-xs text-gray-700">Configure query scope</p>
        </div>
      </div>

      {/* Grade Selection - Horizontal */}
      <div className="space-y-3">
        <label className="text-sm font-semibold text-black flex items-center gap-2">
          <BookOpen size={18} className="text-black" />
          Grade
        </label>
        <div className="grid grid-cols-2 gap-2">
          {grades.map((g) => (
            <button
              key={g.value ?? 'all'}
              onClick={() => setRole({ ...role, grade: g.value })}
              className={`p-3 rounded-lg border-2 text-sm font-semibold transition-all cursor-pointer ${
                role.grade === g.value
                  ? 'bg-amber-200 text-gray-900 border-amber-300 shadow-md'
                  : 'bg-white border-gray-400 text-black hover:bg-gray-100 hover:border-gray-500'
              }`}
            >
              <div className="text-lg">{g.icon}</div>
              <div className="text-xs mt-1 font-semibold">{g.label}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Class Selection - Horizontal */}
      <div className="space-y-3">
        <label className="text-sm font-semibold text-black flex items-center gap-2">
          <Layers size={18} className="text-black" />
          Class
        </label>
        <div className="grid grid-cols-2 gap-2">
          {classes.map((c) => (
            <button
              key={c.value ?? 'all'}
              onClick={() => setRole({ ...role, class: c.value })}
              className={`p-3 rounded-lg border-2 text-sm font-semibold transition-all cursor-pointer ${
                role.class === c.value
                  ? 'bg-amber-200 text-gray-900 border-amber-300 shadow-md'
                  : 'bg-white border-gray-400 text-black hover:bg-gray-100 hover:border-gray-500'
              }`}
            >
              <div className="text-lg">{c.icon}</div>
              <div className="text-xs mt-1 font-semibold">{c.label}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Current Scope Display */}
      <div className="p-4 bg-blue-50 border-2 border-blue-300 rounded-lg space-y-2">
        <p className="text-xs font-bold text-black">📌 Active Scope:</p>
        <div className="flex items-center gap-2 flex-wrap">
          <span className="px-3 py-1 bg-black text-white rounded-lg text-xs font-mono font-semibold">
            {role.grade === null ? 'All Grades' : `Grade ${role.grade}`}
          </span>
          <span className="text-sm text-black font-bold">×</span>
          <span className="px-3 py-1 bg-gray-800 text-white rounded-lg text-xs font-mono font-semibold">
            {role.class === null ? 'All Classes' : `Class ${role.class}`}
          </span>
        </div>
        <p className="text-xs text-gray-700 pt-1">✓ Queries will be filtered by this configuration</p>
      </div>
    </div>
  )
}
