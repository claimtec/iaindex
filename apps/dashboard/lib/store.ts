import { create } from 'zustand';
import type { User, Website } from '@/types';

interface AppState {
  // User state
  user: User | null;
  setUser: (user: User | null) => void;

  // Websites state
  websites: Website[];
  setWebsites: (websites: Website[]) => void;
  addWebsite: (website: Website) => void;
  updateWebsite: (id: string, data: Partial<Website>) => void;
  removeWebsite: (id: string) => void;

  // UI state
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
  toggleSidebar: () => void;
}

export const useStore = create<AppState>((set) => ({
  // User state
  user: null,
  setUser: (user) => set({ user }),

  // Websites state
  websites: [],
  setWebsites: (websites) => set({ websites }),
  addWebsite: (website) =>
    set((state) => ({ websites: [...state.websites, website] })),
  updateWebsite: (id, data) =>
    set((state) => ({
      websites: state.websites.map((w) =>
        w.id === id ? { ...w, ...data } : w
      ),
    })),
  removeWebsite: (id) =>
    set((state) => ({
      websites: state.websites.filter((w) => w.id !== id),
    })),

  // UI state
  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
  toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
}));
