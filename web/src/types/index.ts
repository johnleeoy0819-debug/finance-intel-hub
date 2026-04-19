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

export interface TrendPoint {
  date: string
  count: number
}

export interface SentimentDist {
  sentiment: string
  count: number
}

export interface CategoryDist {
  category_id: number
  name: string
  count: number
}

export interface RecentArticle {
  id: number
  title: string
  sentiment: string
  created_at: string
}

export interface DashboardStats {
  total_count: number
  today_count: number
  week_count: number
  pending_count: number
  source_count: number
  edge_count: number
  trend: TrendPoint[]
  sentiment_distribution: SentimentDist[]
  category_distribution: CategoryDist[]
  recent_articles: RecentArticle[]
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
