'use client';

import { Bell, Menu, Search, User } from 'lucide-react';
import { useStore } from '@/lib/store';
import { Button } from '@/components/ui/button';

export function Header() {
  const { toggleSidebar, user } = useStore();

  return (
    <header className="sticky top-0 z-30 bg-white border-b border-gray-200">
      <div className="flex items-center justify-between px-6 py-4">
        {/* Left side */}
        <div className="flex items-center gap-4">
          <button
            onClick={toggleSidebar}
            className="lg:hidden p-2 rounded-md hover:bg-gray-100"
          >
            <Menu size={20} />
          </button>

          {/* Search */}
          <div className="hidden sm:flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg max-w-md">
            <Search size={18} className="text-gray-400" />
            <input
              type="text"
              placeholder="Search websites..."
              className="bg-transparent border-none outline-none text-sm w-full"
            />
          </div>
        </div>

        {/* Right side */}
        <div className="flex items-center gap-3">
          {/* Notifications */}
          <button className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors">
            <Bell size={20} className="text-gray-600" />
            <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-danger rounded-full" />
          </button>

          {/* User menu */}
          <div className="flex items-center gap-3 pl-3 border-l border-gray-200">
            <div className="hidden sm:block text-right">
              <p className="text-sm font-medium text-gray-900">
                {user?.name || 'User'}
              </p>
              <p className="text-xs text-gray-500">
                {user?.email || 'user@example.com'}
              </p>
            </div>
            <button className="w-10 h-10 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center text-white font-medium">
              {user?.name?.[0]?.toUpperCase() || <User size={20} />}
            </button>
          </div>
        </div>
      </div>
    </header>
  );
}
