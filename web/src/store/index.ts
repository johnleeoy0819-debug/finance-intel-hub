import { create } from 'zustand'
import type { Article, Source, Category, Tag, DashboardStats } from '../types'

interface AppState {
  articles: Article[]
  articleTotal: number
  currentArticle: Article | null
  setArticles: (articles: Article[], total: number) => void
  setCurrentArticle: (article: Article | null) => void
  sources: Source[]
  setSources: (sources: Source[]) => void
  categories: Category[]
  tags: Tag[]
  setCategories: (categories: Category[]) => void
  setTags: (tags: Tag[]) => void
  stats: DashboardStats | null
  setStats: (stats: DashboardStats) => void
  searchQuery: string
  setSearchQuery: (q: string) => void
  selectedCategory: number | null
  setSelectedCategory: (id: number | null) => void
}

export const useStore = create<AppState>((set) => ({
  articles: [],
  articleTotal: 0,
  currentArticle: null,
  setArticles: (articles, total) => set({ articles, articleTotal: total }),
  setCurrentArticle: (article) => set({ currentArticle: article }),
  sources: [],
  setSources: (sources) => set({ sources }),
  categories: [],
  tags: [],
  setCategories: (categories) => set({ categories }),
  setTags: (tags) => set({ tags }),
  stats: null,
  setStats: (stats) => set({ stats }),
  searchQuery: '',
  setSearchQuery: (q) => set({ searchQuery: q }),
  selectedCategory: null,
  setSelectedCategory: (id) => set({ selectedCategory: id }),
}))
