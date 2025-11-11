/**
 * Header Component
 * Simple top navigation bar
 *
 * @component
 * @returns {JSX.Element} Header navigation component
 */

import React from 'react'
import { Menu, Settings } from 'lucide-react'

/**
 * Header Component - Simple navigation
 * @returns {JSX.Element}
 */
const Header = () => {
  return (
    <header className="w-full border-b border-gray-300 sticky top-0 z-50 bg-white">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo & Brand */}
          <div className="flex items-center gap-3">
            <div className="text-2xl font-bold text-black">Dumroo AI</div>
            <div className="text-sm text-gray-600">Query System</div>
          </div>


        </div>
      </div>
    </header>
  )
}

export default Header

