/** 获取后端服务根地址（每次调用，避免模块加载时 hostname 固定） */
export function getServerBase(): string {
  if (import.meta.env.VITE_SERVER_URL) {
    return import.meta.env.VITE_SERVER_URL.replace(/\/$/, '')
  }
  // 开发模式：使用相对路径，走 Vite 代理，兼容 localhost / 127.0.0.1 / 局域网 IP
  if (import.meta.env.DEV) {
    return ''
  }
  if (typeof window !== 'undefined') {
    return `http://${window.location.hostname}:8765`
  }
  return 'http://127.0.0.1:8765'
}

/** 获取 API 基础路径 */
function getApiBase(): string {
  const base = getServerBase()
  return base ? `${base}/api` : '/api'
}

export interface SoftwareInfo {
  name: string
  slogan: string
  version: string
  description: string
}

export interface Scheme {
  id: number
  level: string
  title: string
  markdown: string
}

export interface GenerateResult {
  success: boolean
  image_url: string
  raw_image_url: string
  message: string
}

/** 解析 API 错误信息 */
function parseApiError(err: unknown, fallback = '请求失败'): string {
  if (!err || typeof err !== 'object') return fallback
  const detail = (err as { detail?: unknown }).detail
  if (typeof detail === 'string') return detail
  if (Array.isArray(detail)) {
    return detail.map((d) => (typeof d === 'object' && d && 'msg' in d ? String(d.msg) : String(d))).join('; ')
  }
  return fallback
}

/** 将相对路径转为完整图片 URL */
export function resolveImageUrl(path: string): string {
  if (!path) return ''
  if (path.startsWith('http://') || path.startsWith('https://') || path.startsWith('blob:')) return path
  const base = getServerBase()
  const normalized = path.startsWith('/') ? path : `/${path}`
  return base ? `${base}${normalized}` : normalized
}

/** 获取软件信息 */
export async function fetchSoftware(): Promise<SoftwareInfo> {
  const resp = await fetch(`${getApiBase()}/software`)
  if (!resp.ok) throw new Error('无法连接后端服务，请确认 server 已启动')
  return resp.json()
}

/** 获取所有方案 */
export async function fetchSchemes(): Promise<Scheme[]> {
  const resp = await fetch(`${getApiBase()}/schemes`)
  if (!resp.ok) throw new Error('获取方案失败')
  return resp.json()
}

/** 选择等级 */
export async function selectLevel(level: string) {
  await fetch(`${getApiBase()}/schemes/${level}/select`, { method: 'POST' })
}

/** 拉取图片并转为 blob URL，确保前端能稳定显示 */
async function fetchImageAsBlobUrl(imagePath: string): Promise<string> {
  const fullUrl = `${resolveImageUrl(imagePath)}?t=${Date.now()}`
  const imgResp = await fetch(fullUrl)
  if (!imgResp.ok) {
    throw new Error(`图片加载失败 (${imgResp.status})，请检查后端 static 目录`)
  }
  const blob = await imgResp.blob()
  if (!blob.size) {
    throw new Error('生成的图片为空，请重试')
  }
  return URL.createObjectURL(blob)
}

/** 上传图片并生成 */
export async function generateImage(level: string, file: File): Promise<GenerateResult> {
  const formData = new FormData()
  formData.append('level', level)
  formData.append('image', file, file.name || 'photo.jpg')

  let resp: Response
  try {
    resp = await fetch(`${getApiBase()}/generate`, { method: 'POST', body: formData })
  } catch {
    const hint = import.meta.env.DEV
      ? '无法连接后端。请确认 server 已启动（端口 8765），并用同一地址访问页面（localhost 或 127.0.0.1 均可）'
      : '无法连接后端服务，请先启动 server（端口 8765）'
    throw new Error(hint)
  }

  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}))
    throw new Error(parseApiError(err, `生成失败 (${resp.status})`))
  }

  const result = await resp.json()
  const rawPath = result.image_url as string
  if (!rawPath) {
    throw new Error('服务器未返回图片地址')
  }

  const displayUrl = await fetchImageAsBlobUrl(rawPath)

  return {
    success: result.success,
    image_url: displayUrl,
    raw_image_url: resolveImageUrl(rawPath),
    message: result.message || '变身完成！',
  }
}

/** 释放 blob URL 占用的内存 */
export function revokeBlobUrl(url: string | null) {
  if (url && url.startsWith('blob:')) {
    URL.revokeObjectURL(url)
  }
}

/** 提交反馈 */
export async function submitFeedback(data: {
  level: string
  is_valid: boolean | null
  content: string
  image_path: string
}) {
  let resp: Response
  try {
    resp = await fetch(`${getApiBase()}/feedback`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    })
  } catch {
    throw new Error('无法连接后端，请确认 server 已启动')
  }
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}))
    throw new Error(parseApiError(err, '反馈提交失败'))
  }
  return resp.json()
}

/** 下载图片 */
export async function downloadImage(imageUrl: string, filename: string) {
  if (imageUrl.startsWith('blob:')) {
    const a = document.createElement('a')
    a.href = imageUrl
    a.download = filename
    a.click()
    return { success: true }
  }

  const fullUrl = resolveImageUrl(imageUrl)
  if (window.electronAPI?.isElectron) {
    return window.electronAPI.saveImage(fullUrl, filename)
  }
  const resp = await fetch(fullUrl)
  if (!resp.ok) throw new Error('下载失败')
  const blob = await resp.blob()
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
  return { success: true }
}

