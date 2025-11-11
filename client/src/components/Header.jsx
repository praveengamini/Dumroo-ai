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

          {/* Right: Actions */}
          <div className="flex items-center gap-2 sm:gap-3">
            <button className="hidden sm:flex items-center gap-2 px-4 py-2 rounded border border-gray-300 hover:bg-gray-100 transition-smooth text-black">
              <Settings size={18} />
              <span className="text-sm">Settings</span>
            </button>
            <button className="px-3 sm:px-4 py-2 rounded border-2 border-black bg-black text-white hover:bg-gray-800 font-medium transition-smooth text-sm">
              Connect
            </button>
            <button className="p-2 hover:bg-gray-100 rounded transition-smooth lg:hidden text-black">
              <Menu size={20} />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header

