import axios from 'axios'
import type { Article, Source, UploadTask, DashboardStats } from '../types'

const api = axios.create({
  baseURL: '/api',
  headers: { 'Content-Type': 'application/json' },
})

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
}

export const statsApi = {
  dashboard: () => api.get<DashboardStats>('/stats/dashboard').then(r => r.data),
}

export const uploadApi = {
  upload: (file: File) => {
    const form = new FormData()
    form.append('file', file)
    return api.post<UploadTask>('/upload', form, { headers: { 'Content-Type': 'multipart/form-data' } }).then(r => r.data)
  },
  tasks: () => api.get<UploadTask[]>('/upload/tasks').then(r => r.data),
}
