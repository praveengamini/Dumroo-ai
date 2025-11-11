import React, { useState } from 'react'
import Header from './components/Header'
import RoleSelector from './components/RoleSelector'
import ChatPanel from './components/ChatPanel'
import Dashboard from './components/Dashboard'
import ResultsPanel from './components/ResultsPanel'
import { v4 as uuidv4 } from 'uuid'
import './styles/theme.css'

export default function App() {
  const [role, setRole] = useState({ grade: null, class: null })
  const [sessionId] = useState(uuidv4())
  const [messages, setMessages] = useState([])
  const [results, setResults] = useState([])
  const [condition, setCondition] = useState('')

  return (
    <div className="min-h-screen flex flex-col bg-white">
      {/* Header */}
      <Header />

      {/* Main Content */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-4 sm:px-6 py-6 lg:py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Sidebar - Small */}
          <div className="lg:col-span-2 space-y-4">
            {/* Role Selector - Compact */}
            <div className="glass rounded-lg p-4 border border-gray-300">
              <RoleSelector role={role} setRole={setRole} />
            </div>
          </div>

          {/* Middle/Main Area - Query & Results */}
          <div className="lg:col-span-10 space-y-6">
            {/* Chat Panel - PRIMARY FOCUS */}
            <div className="glass rounded-lg p-6 border border-gray-300 bg-white">
              <ChatPanel
                role={role}
                sessionId={sessionId}
                messages={messages}
                setMessages={setMessages}
                setResults={setResults}
                setCondition={setCondition}
              />
            </div>

            {/* Dashboard */}
            <div className="glass rounded-lg p-6 border border-gray-300 bg-white">
              <Dashboard results={results} condition={condition} />
            </div>

            {/* Results Panel */}
            <div className="glass rounded-lg border border-gray-300 bg-white">
              <ResultsPanel results={results} />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full border-t border-gray-300 bg-gray-50 px-6 py-4 text-center text-xs text-gray-700">
        <p>Dumroo AI • Powered by Gemini • {new Date().getFullYear()}</p>
      </footer>
    </div>
  )
}
