const API_BASE = import.meta.env.VITE_SERVER_URL
  ? `${import.meta.env.VITE_SERVER_URL.replace(/\/$/, '')}/api`
  : '/api'

/** 认证失败错误 */
export class AuthError extends Error {
  constructor(message = '登录已失效') {
    super(message)
    this.name = 'AuthError'
  }
}

/** 获取存储的管理员 token */
export function getToken(): string {
  return localStorage.getItem('lolida_admin_token') || ''
}

/** 设置管理员 token */
export function setToken(token: string) {
  localStorage.setItem('lolida_admin_token', token)
}

/** 清除 token */
export function clearToken() {
  localStorage.removeItem('lolida_admin_token')
}

/** 通用 API 请求 */
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getToken()
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  let resp: Response
  try {
    resp = await fetch(`${API_BASE}${path}`, { ...options, headers })
  } catch {
    throw new Error('无法连接后端，请确认 server 已启动（端口 8765）')
  }

  if (resp.status === 401) {
    clearToken()
    throw new AuthError('登录已失效，请重新登录')
  }

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }))
    const detail = err.detail
    throw new Error(typeof detail === 'string' ? detail : '请求失败')
  }
  return resp.json()
}

export interface Scheme {
  id: number
  level: string
  title: string
  markdown: string
  prompt_template: string
  created_at: string
  updated_at: string
}

export interface Feedback {
  id: number
  level: string
  is_valid: boolean | null
  content: string
  image_path: string
  processed: boolean
  created_at: string
}

export interface LevelStat {
  level: string
  label: string
  select_count: number
  generate_count: number
}

/** 管理员登录 */
export async function adminLogin(password: string) {
  return request<{ success: boolean; token: string }>('/admin/login', {
    method: 'POST',
    body: JSON.stringify({ password }),
  })
}

/** 获取所有方案 */
export async function fetchSchemes() {
  return request<Scheme[]>('/admin/schemes')
}

/** 更新方案 */
export async function updateScheme(level: string, data: Partial<Scheme>) {
  return request<Scheme>(`/admin/schemes/${level}`, {
    method: 'PUT',
    body: JSON.stringify(data),
  })
}

/** AI 重新生成方案 */
export async function regenerateScheme(level: string) {
  return request<Scheme>(`/admin/schemes/${level}/regenerate`, { method: 'POST' })
}

/** 删除方案 */
export async function deleteScheme(level: string) {
  return request<{ success: boolean }>(`/admin/schemes/${level}`, { method: 'DELETE' })
}

/** 获取反馈列表 */
export async function fetchFeedback() {
  return request<Feedback[]>('/admin/feedback')
}

/** 标记反馈已处理 */
export async function processFeedback(id: number, processed = true) {
  return request<Feedback>(`/admin/feedback/${id}`, {
    method: 'PATCH',
    body: JSON.stringify({ processed }),
  })
}

/** 获取统计数据 */
export async function fetchStats() {
  return request<LevelStat[]>('/stats')
}
