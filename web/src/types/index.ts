export interface Article {
  id: number
  title: string
  url?: string
  source?: string
  author?: string
  published_at?: string
  summary?: string
  key_points?: string[]
  entities?: string[]
  sentiment?: 'positive' | 'neutral' | 'negative'
  importance?: 'high' | 'medium' | 'low'
  primary_category?: string
  secondary_category?: string
  tags?: string[]
  clean_content?: string
  mindmap?: string
  status: string
  created_at: string
}

export interface Category {
  id: number
  parent_id?: number
  name: string
  slug: string
  sort_order: number
}

export interface Tag {
  id: number
  name: string
  usage_count: number
}

export interface Source {
  id: number
  name: string
  url: string
  driver: string
  schedule?: string
  is_active: boolean
  last_crawled_at?: string
}

export interface UploadTask {
  id: number
  original_filename: string
  file_type: string
  status: string
  article_id?: number
  created_at: string
}

export interface DashboardStats {
  today_count: number
  week_count: number
  pending_count: number
  source_count: number
}
