import { useEffect, useState } from 'react'
import { RefreshCw, Save, Trash2, Wand2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Input } from '@/components/ui/input'
import {
  AuthError,
  type Scheme,
  deleteScheme,
  fetchSchemes,
  regenerateScheme,
  updateScheme,
} from '@/lib/api'

interface SchemesPageProps {
  onAuthError?: (err: unknown) => void
}

/** 方案管理页 */
export function SchemesPage({ onAuthError }: SchemesPageProps) {
  const [schemes, setSchemes] = useState<Scheme[]>([])
  const [selected, setSelected] = useState<Scheme | null>(null)
  const [loading, setLoading] = useState(false)
  const [pageLoading, setPageLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  /** 加载方案列表 */
  const loadSchemes = async () => {
    setPageLoading(true)
    setError('')
    try {
      const data = await fetchSchemes()
      setSchemes(data)
      if (data.length > 0) {
        setSelected((prev) => prev ?? data[0])
      }
    } catch (e) {
      if (e instanceof AuthError) {
        onAuthError?.(e)
        return
      }
      setError(e instanceof Error ? e.message : '加载失败')
    } finally {
      setPageLoading(false)
    }
  }

  useEffect(() => {
    loadSchemes()
  }, [])

  /** 保存当前编辑的方案 */
  const handleSave = async () => {
    if (!selected) return
    setLoading(true)
    try {
      const updated = await updateScheme(selected.level, {
        title: selected.title,
        markdown: selected.markdown,
        prompt_template: selected.prompt_template,
      })
      setSelected(updated)
      setMessage('保存成功！')
      await loadSchemes()
    } catch (e) {
      if (e instanceof AuthError) { onAuthError?.(e); return }
      setMessage(`保存失败: ${e}`)
    } finally {
      setLoading(false)
    }
  }

  /** AI 重新生成方案 */
  const handleRegenerate = async () => {
    if (!selected) return
    setLoading(true)
    setMessage('AI 正在生成方案，请稍候...')
    try {
      const updated = await regenerateScheme(selected.level)
      setSelected(updated)
      setMessage('AI 重新生成完成！')
      await loadSchemes()
    } catch (e) {
      if (e instanceof AuthError) { onAuthError?.(e); return }
      setMessage(`AI 生成失败: ${e}`)
    } finally {
      setLoading(false)
    }
  }

  /** 删除方案 */
  const handleDelete = async () => {
    if (!selected || !confirm(`确定删除 ${selected.level} 方案？`)) return
    try {
      await deleteScheme(selected.level)
      setSelected(null)
      await loadSchemes()
      setMessage('已删除')
    } catch (e) {
      if (e instanceof AuthError) { onAuthError?.(e); return }
      setMessage(`删除失败: ${e}`)
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-pink-600">📋 方案管理</h2>

      {pageLoading && (
        <p className="text-sm text-purple-500 bg-purple-50 p-3 rounded-xl">加载方案中...</p>
      )}
      {error && (
        <div className="text-sm text-red-600 bg-red-50 p-3 rounded-xl flex items-center justify-between gap-2">
          <span>{error}</span>
          <Button size="sm" variant="outline" onClick={loadSchemes}>重试</Button>
        </div>
      )}
      {message && <p className="text-sm text-purple-600 bg-purple-50 p-2 rounded-lg">{message}</p>}

      {!pageLoading && schemes.length === 0 && !error && (
        <p className="text-center text-gray-400 py-8">暂无方案数据，请确认后端已启动并完成初始化</p>
      )}

      <div className="flex flex-wrap gap-2">
        {schemes.map((s) => (
          <Button
            key={s.level}
            variant={selected?.level === s.level ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelected(s)}
          >
            {s.level}
          </Button>
        ))}
      </div>

      {selected && (
        <Card>
          <CardHeader>
            <CardTitle>{selected.level} - {selected.title}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <label className="text-sm font-bold text-pink-500">标题</label>
              <Input
                value={selected.title}
                onChange={(e) => setSelected({ ...selected, title: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm font-bold text-pink-500">Markdown 内容（含「效果描述」）</label>
              <Textarea
                className="min-h-[300px]"
                value={selected.markdown}
                onChange={(e) => setSelected({ ...selected, markdown: e.target.value })}
              />
            </div>
            <div>
              <label className="text-sm font-bold text-pink-500">Prompt 模板（备用）</label>
              <Textarea
                value={selected.prompt_template}
                onChange={(e) => setSelected({ ...selected, prompt_template: e.target.value })}
              />
            </div>
            <div className="flex flex-wrap gap-2">
              <Button onClick={handleSave} disabled={loading}>
                <Save className="w-4 h-4" /> 保存
              </Button>
              <Button variant="secondary" onClick={handleRegenerate} disabled={loading}>
                <Wand2 className="w-4 h-4" /> AI 重新生成
              </Button>
              <Button variant="danger" onClick={handleDelete}>
                <Trash2 className="w-4 h-4" /> 删除
              </Button>
              <Button variant="ghost" onClick={loadSchemes}>
                <RefreshCw className="w-4 h-4" /> 刷新
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
