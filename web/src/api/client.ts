import axios from 'axios'
import type { Article, Source, UploadTask, DashboardStats } from '../types'

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

export const searchApi = {
  search: (q: string) => api.get('/search', { params: { q } }).then(r => r.data),
  semantic: (q: string) => api.get('/search/semantic', { params: { q } }).then(r => r.data),
  hybrid: (q: string) => api.get('/search/hybrid', { params: { q } }).then(r => r.data),
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

export const skillApi = {
  feedback: (data: { skill_name?: string; query: string; response_summary?: string; rating?: number; comment?: string }) =>
    api.post('/skill/feedback', data).then(r => r.data),
  examples: (field?: string) => api.get('/skill/examples', { params: { field } }).then(r => r.data),
}
