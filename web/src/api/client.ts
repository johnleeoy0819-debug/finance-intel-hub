import axios from 'axios'
import type { Article, Source, UploadTask, DashboardStats, Category, Tag, WikiPage, LintReport } from '../types'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail
    const message =
      typeof detail === 'string'
        ? detail
        : Array.isArray(detail)
          ? detail.map((d: any) => d.msg || d).join('; ')
          : error.message || '请求失败，请稍后重试'
    return Promise.reject(new Error(message))
  }
)

export const articlesApi = {
  list: (params?: { category_id?: number; tag?: string; limit?: number; offset?: number }) =>
    api.get<{ total: number; items: Article[] }>('/articles', { params }).then(r => r.data),
  get: (id: number) => api.get<Article>(`/articles/${id}`).then(r => r.data),
  delete: (id: number) => api.delete(`/articles/${id}`),
  related: (id: number) => api.get<Article[]>(`/articles/${id}/related`).then(r => r.data),
}

export const sourcesApi = {
  list: () => api.get<Source[]>('/crawler/sources').then(r => r.data),
  create: (data: Partial<Source>) => api.post<Source>('/crawler/sources', data).then(r => r.data),
  update: (id: number, data: Partial<Source>) => api.put<Source>(`/crawler/sources/${id}`, data).then(r => r.data),
  delete: (id: number) => api.delete(`/crawler/sources/${id}`),
  trigger: (id: number) => api.post<{ article_ids: number[] }>(`/crawler/trigger/${id}`).then(r => r.data),
}

export interface SearchResultItem {
  article: Article
  score?: number
  mode: string
}

export const searchApi = {
  search: (q: string) => api.get<{ query: string; items: SearchResultItem[]; mode: string }>('/search', { params: { q } }).then(r => r.data),
  semantic: (q: string) => api.get<{ query: string; items: SearchResultItem[]; mode: string }>('/search/semantic', { params: { q } }).then(r => r.data),
  hybrid: (q: string) => api.get<{ query: string; items: SearchResultItem[]; mode: string }>('/search/hybrid', { params: { q } }).then(r => r.data),
}


export const statsApi = {
  dashboard: () => api.get<DashboardStats>('/stats/dashboard').then(r => r.data),
}

export const uploadApi = {
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post<any>('/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data)
  },
  uploadUrl: (url: string) => api.post<{ task_id: number; status: string; type: string }>('/upload/url', { url }).then(r => r.data),
  tasks: () => api.get<UploadTask[]>('/upload/tasks').then(r => r.data),
}

export interface GraphNode {
  id: number
  title: string
  category?: number
  sentiment?: string
}

export interface GraphLink {
  source: number
  target: number
  type: string
  strength?: number
  reason?: string
}

export interface GraphData {
  center_id?: number
  nodes: GraphNode[]
  links: GraphLink[]
}

export const graphApi = {
  article: (id: number, depth?: number) =>
    api.get<GraphData>(`/graph/articles/${id}`, { params: { depth } }).then(r => r.data),
  global: (limit?: number) =>
    api.get<GraphData>('/graph/global', { params: { limit } }).then(r => r.data),
}

export interface Publication {
  id: number
  pub_type: string
  title: string
  authors?: string
  publisher?: string
  doi?: string
  url?: string
  abstract?: string
  keywords?: string
  publication_date?: string
  citation_count: number
  created_at: string
}

export const publicationsApi = {
  list: (params?: { pub_type?: string; q?: string; limit?: number; offset?: number }) =>
    api.get<{ total: number; items: Publication[] }>('/publications', { params }).then(r => r.data),
  get: (id: number) => api.get<{ publication: Publication; chapters: any[] }>(`/publications/${id}`).then(r => r.data),
  import: (url: string) => api.post<{ publication: Publication; created: boolean }>('/publications/import', null, { params: { url } }).then(r => r.data),
  delete: (id: number) => api.delete(`/publications/${id}`),
}

export const categoriesApi = {
  list: () => api.get<Category[]>('/categories').then(r => r.data),
}

export const lintApi = {
  list: () => api.get<LintReport[]>('/lint/reports').then(r => r.data),
  summary: () => api.get<{ total_open: number; by_type: Record<string, number> }>('/lint/summary').then(r => r.data),
  run: () => api.post('/lint/run').then(r => r.data),
  update: (id: number, status: string) => api.put(`/lint/reports/${id}`, { status }).then(r => r.data),
}

export const wikiApi = {
  list: () => api.get<WikiPage[]>('/wiki').then(r => r.data),
  get: (slug: string) => api.get<WikiPage>(`/wiki/${slug}`).then(r => r.data),
  compile: (topic: string, article_ids?: number[]) => api.post('/wiki/compile', { topic, article_ids }).then(r => r.data),
  writeback: (title: string, content: string, source_query?: string) =>
    api.post('/wiki/writeback', { title, content, source_query }).then(r => r.data),
}

export const tagsApi = {
  list: (q?: string) => api.get<Tag[]>('/tags', { params: { q } }).then(r => r.data),
}

export const settingsApi = {
  getRules: () => api.get<{ rules: string }>('/settings/rules').then(r => r.data),
  updateRules: (rules: string) => api.put('/settings/rules', { rules }).then(r => r.data),
}

export const operationsApi = {
  list: (params?: { operation_type?: string; limit?: number; offset?: number }) =>
    api.get<{ total: number; items: any[] }>('/operations', { params }).then(r => r.data),
}

export const exportApi = {
  wiki: () => api.post('/export/wiki').then(r => r.data),
  all: () => api.post('/export/all').then(r => r.data),
  git: () => api.post('/export/git').then(r => r.data),
}

export const skillApi = {
  chat: (query: string) => api.post<{ query: string; answer: string; strategy: string; wiki_slug?: string; sources: { id: number; title: string }[] }>('/skill/chat', { query }).then(r => r.data),
  feedback: (data: { skill_name?: string; query: string; response_summary?: string; rating?: number; comment?: string }) =>
    api.post('/skill/feedback', data).then(r => r.data),
  examples: (field?: string) => api.get('/skill/examples', { params: { field } }).then(r => r.data),
}
