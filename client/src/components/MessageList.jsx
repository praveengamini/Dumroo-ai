import React, { useRef, useEffect } from 'react'
import { CheckCircle2, XCircle, Bot } from 'lucide-react'

export default function MessageList({ messages }) {
  const ref = useRef()
  
  useEffect(() => {
    if (ref.current) ref.current.scrollTop = ref.current.scrollHeight
  }, [messages])

  const formatTime = (timestamp) => {
    if (!timestamp) return ''
    return new Date(timestamp).toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div ref={ref} className="h-full overflow-y-auto p-4 space-y-3">
      {messages.length === 0 && (
        <div className="flex items-center justify-center h-full text-center">
          <div className="text-gray-700">
            <Bot size={32} className="mx-auto mb-3 text-gray-600" />
            <p className="text-sm font-medium text-black">Start a conversation</p>
            <p className="text-xs mt-1 text-gray-700">Ask about students, grades, or homework</p>
          </div>
        </div>
      )}
      
      {messages.map((m, i) => (
        <div 
          key={i} 
          className={`flex gap-2 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
        >
          {m.sender === 'bot' && (
            <div className="w-6 h-6 rounded-full bg-gray-200 flex items-center justify-center shrink-0 mt-1">
              <Bot size={14} className="text-black" />
            </div>
          )}
          
          <div className={`max-w-xs lg:max-w-sm px-4 py-3 rounded ${
            m.sender === 'user' 
              ? 'bg-blue-500 text-white rounded-br-none'
              : m.isError
              ? 'bg-red-100 text-red-900 rounded-bl-none border border-red-300'
              : 'bg-gray-100 text-gray-900 rounded-bl-none border border-gray-300'
          }`}>
            <div className="text-sm whitespace-pre-wrap wrap-break-word leading-relaxed font-medium">
              {m.text}
            </div>
            {m.count !== undefined && (
              <div className="mt-2 pt-2 border-t border-blue-400 text-xs font-semibold text-white">
                ✓ {m.count} result{m.count !== 1 ? 's' : ''} found
              </div>
            )}
            <div className={`text-xs mt-2 ${m.sender === 'user' ? 'text-blue-100' : 'text-gray-600'}`}>
              {formatTime(m.timestamp)}
            </div>
          </div>
          
          {m.sender === 'user' && (
            <div className="w-6 h-6 rounded-full bg-black flex items-center justify-center shrink-0 mt-1 text-xs font-bold text-white">
              U
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
