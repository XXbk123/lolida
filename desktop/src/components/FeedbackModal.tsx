import { MessageSquare, Send, X } from 'lucide-react'
import { cn, LEVEL_CONFIG } from '@/lib/utils'

interface FeedbackModalProps {
  open: boolean
  onClose: () => void
  selectedLevel: string
  onLevelChange: (level: string) => void
  feedbackText: string
  onFeedbackTextChange: (text: string) => void
  feedbackRating: boolean | null
  onFeedbackRatingChange: (rating: boolean | null) => void
  onSubmit: () => void
  submitting: boolean
  hasResult: boolean
}

/** 用户意见反馈弹窗 */
export function FeedbackModal({
  open,
  onClose,
  selectedLevel,
  onLevelChange,
  feedbackText,
  onFeedbackTextChange,
  feedbackRating,
  onFeedbackRatingChange,
  onSubmit,
  submitting,
  hasResult,
}: FeedbackModalProps) {
  if (!open) return null

  return (
    <div className="fixed inset-0 bg-black/40 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl p-6 max-w-md w-full border-2 border-pink-200 shadow-2xl">
        <div className="flex items-center justify-between mb-4">
          <h3 className="font-bold text-pink-600 flex items-center gap-2 text-lg">
            <MessageSquare className="w-5 h-5" /> 意见反馈
          </h3>
          <button
            onClick={onClose}
            className="p-1 rounded-lg hover:bg-pink-50 cursor-pointer text-gray-400 hover:text-pink-500"
            aria-label="关闭"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <p className="text-sm text-gray-500 mb-4">
          兄弟有什么想说的？你的意见帮我们变得更好~
          {hasResult && <span className="text-purple-500"> （已关联本次变身结果）</span>}
        </p>

        {/* 关联等级 */}
        <div className="mb-4">
          <label className="text-xs font-bold text-pink-500 mb-2 block">相关等级</label>
          <div className="flex flex-wrap gap-2">
            {LEVEL_CONFIG.map((l) => (
              <button
                key={l.level}
                type="button"
                onClick={() => onLevelChange(l.level)}
                className={cn(
                  'px-3 py-1 rounded-lg text-xs font-bold border-2 cursor-pointer transition-all',
                  selectedLevel === l.level
                    ? 'border-pink-500 bg-pink-100 text-pink-600'
                    : 'border-pink-200 text-gray-500 hover:bg-pink-50'
                )}
              >
                {l.emoji} {l.level}
              </button>
            ))}
          </div>
        </div>

        {/* 有效 / 无效 */}
        <div className="mb-4">
          <label className="text-xs font-bold text-pink-500 mb-2 block">方案评价（可选）</label>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() => onFeedbackRatingChange(feedbackRating === true ? null : true)}
              className={cn(
                'flex-1 py-2 rounded-xl text-sm font-bold border-2 cursor-pointer transition-all',
                feedbackRating === true
                  ? 'border-green-500 bg-green-50 text-green-600'
                  : 'border-gray-200 text-gray-500 hover:border-green-300'
              )}
            >
              👍 有效
            </button>
            <button
              type="button"
              onClick={() => onFeedbackRatingChange(feedbackRating === false ? null : false)}
              className={cn(
                'flex-1 py-2 rounded-xl text-sm font-bold border-2 cursor-pointer transition-all',
                feedbackRating === false
                  ? 'border-red-400 bg-red-50 text-red-500'
                  : 'border-gray-200 text-gray-500 hover:border-red-300'
              )}
            >
              👎 无效
            </button>
          </div>
        </div>

        {/* 文字反馈 */}
        <textarea
          className="w-full border-2 border-pink-200 rounded-xl p-3 text-sm min-h-[120px] focus:border-pink-400 focus:outline-none resize-none"
          placeholder="说说你的想法：效果怎么样？有什么建议？"
          value={feedbackText}
          onChange={(e) => onFeedbackTextChange(e.target.value)}
        />

        <div className="flex gap-2 mt-4">
          <button
            onClick={onSubmit}
            disabled={submitting || !feedbackText.trim()}
            className={cn(
              'flex-1 py-2.5 rounded-xl font-bold text-white flex items-center justify-center gap-2 cursor-pointer',
              'bg-gradient-to-r from-pink-500 to-purple-500 hover:from-pink-600 hover:to-purple-600',
              'disabled:opacity-50 disabled:cursor-not-allowed'
            )}
          >
            <Send className="w-4 h-4" />
            {submitting ? '提交中...' : '提交反馈'}
          </button>
          <button
            onClick={onClose}
            className="py-2.5 px-4 rounded-xl border-2 border-gray-200 cursor-pointer hover:bg-gray-50 font-bold text-gray-500"
          >
            取消
          </button>
        </div>
      </div>
    </div>
  )
}
