import { useEffect, useState } from 'react'
import { CheckCircle, RefreshCw, XCircle } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { AuthError, type Feedback, fetchFeedback, processFeedback } from '@/lib/api'

interface FeedbackPageProps {
  onAuthError?: (err: unknown) => void
}

/** 用户反馈管理页 */
export function FeedbackPage({ onAuthError }: FeedbackPageProps) {
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([])
  const [filter, setFilter] = useState<'all' | 'pending' | 'processed'>('all')

  /** 加载反馈列表 */
  const loadFeedback = async () => {
    try {
      const data = await fetchFeedback()
      setFeedbacks(data)
    } catch (e) {
      if (e instanceof AuthError) onAuthError?.(e)
    }
  }

  useEffect(() => {
    loadFeedback()
  }, [])

  /** 标记反馈已处理 */
  const handleProcess = async (id: number) => {
    await processFeedback(id, true)
    await loadFeedback()
  }

  const filtered = feedbacks.filter((f) => {
    if (filter === 'pending') return !f.processed
    if (filter === 'processed') return f.processed
    return true
  })

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-pink-600">💬 用户反馈</h2>

      <div className="flex gap-2 items-center">
        {(['all', 'pending', 'processed'] as const).map((f) => (
          <Button key={f} variant={filter === f ? 'default' : 'outline'} size="sm" onClick={() => setFilter(f)}>
            {f === 'all' ? '全部' : f === 'pending' ? '待处理' : '已处理'}
          </Button>
        ))}
        <Button variant="ghost" size="sm" onClick={loadFeedback}>
          <RefreshCw className="w-4 h-4" /> 刷新
        </Button>
      </div>

      <div className="space-y-3">
        {filtered.map((fb) => (
          <Card key={fb.id} className={fb.processed ? 'opacity-60' : ''}>
            <CardContent className="p-4">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <span className="font-bold text-pink-600">{fb.level || '未知等级'}</span>
                    {fb.is_valid === true && <CheckCircle className="w-4 h-4 text-green-500" />}
                    {fb.is_valid === false && <XCircle className="w-4 h-4 text-red-500" />}
                    <span className="text-xs text-gray-400">
                      {new Date(fb.created_at).toLocaleString('zh-CN')}
                    </span>
                  </div>
                  <p className="text-sm text-gray-700">{fb.content || '（无文字反馈）'}</p>
                  {fb.image_path && (
                    <div className="mt-2">
                      <img
                        src={fb.image_path.startsWith('http') ? fb.image_path : `http://127.0.0.1:8765${fb.image_path}`}
                        alt="反馈关联图片"
                        className="max-h-24 rounded-lg border border-pink-100"
                        onError={(e) => { (e.target as HTMLImageElement).style.display = 'none' }}
                      />
                    </div>
                  )}
                </div>
                {!fb.processed && (
                  <Button size="sm" onClick={() => handleProcess(fb.id)}>
                    标记已处理
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ))}
        {filtered.length === 0 && (
          <p className="text-center text-gray-400 py-8">暂无反馈，兄弟们还在观望~</p>
        )}
      </div>
    </div>
  )
}
