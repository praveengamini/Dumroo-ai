import React, { useState, useRef, useEffect } from 'react'
import { Send, Loader2, AlertCircle } from 'lucide-react'
import MessageList from './MessageList'
import api from '../lib/apis'

export default function ChatPanel({ role, sessionId, messages, setMessages, setResults, setCondition }) {
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const inputRef = useRef(null)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async (e) => {
    e?.preventDefault()
    if (!input.trim()) return
    
    setError('')
    const userMsg = { sender: 'user', text: input, timestamp: new Date() }
    setMessages(prev => [...prev, userMsg])
    setInput('')
    setLoading(true)

    try {
      const res = await api.postQuery({ 
        query: input, 
        role: { grade: role.grade, class_name: role.class }, 
        sessionId 
      })
      if (res.error) {
        setError(res.error)
        setMessages(prev => [...prev, { 
          sender: 'bot', 
          text: '❌ Error: ' + res.error,
          timestamp: new Date(),
          isError: true 
        }])
      } else {
        const cond = res.condition || ''
        setCondition(cond)
        setResults(res.results || [])
        setMessages(prev => [
          ...prev,
          { 
            sender: 'bot', 
            text: `✅ Found ${res.count || 0} result(s)\nFilter: \`${cond}\``,
            timestamp: new Date(),
            count: res.count
          },
        ])
      }
    } catch (err) {
      setError(err.message || 'Network error')
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: '⚠️ Network error - Please try again',
        timestamp: new Date(),
        isError: true
      }])
    } finally {
      setLoading(false)
      inputRef.current?.focus()
    }
  }

  return (
    <div className="flex flex-col h-96 bg-white border border-gray-300 rounded overflow-hidden">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-300 bg-gray-50">
        <h3 className="font-semibold text-black">Query Assistant</h3>
        <p className="text-xs text-gray-600 mt-1">Ask about students, grades, or homework</p>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3 bg-white">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500 text-sm text-center">
            <div>
              <p className="mb-2">💬 No messages yet</p>
              <p className="text-xs">Ask about students, grades, or homework status</p>
            </div>
          </div>
        ) : (
          <>
            <MessageList messages={messages} />
            <div ref={messagesEndRef} />
          </>
        )}
      </div>

      {/* Error Display */}
      {error && (
        <div className="px-4 py-2 bg-red-50 border-l-2 border-red-300 text-red-700 text-sm flex items-start gap-2">
          <AlertCircle size={16} className="mt-0.5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSend} className="p-4 border-t border-gray-300 bg-gray-50">
        <div className="flex items-end gap-2">
          <input
            ref={inputRef}
            className="flex-1 p-3 rounded border border-gray-400 text-black placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-black text-sm font-medium"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask: 'Which students haven't submitted homework?'"
            disabled={loading}
          />
          <button
            type="submit"
            className="p-3 rounded-lg bg-black text-white font-semibold hover:bg-gray-900 disabled:bg-gray-400 transition-smooth disabled:cursor-not-allowed flex items-center justify-center"
            disabled={loading || !input.trim()}
            title={loading ? 'Thinking...' : 'Send query'}
          >
            {loading ? (
              <Loader2 size={18} className="animate-spin" />
            ) : (
              <Send size={18} />
            )}
          </button>
        </div>
        {loading && (
          <p className="text-xs text-gray-700 mt-2 flex items-center gap-2">
            <Loader2 size={12} className="animate-spin" />
            Processing your query with AI...
          </p>
        )}
      </form>
    </div>
  )
}
