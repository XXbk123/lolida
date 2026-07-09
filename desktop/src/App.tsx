import { useCallback, useEffect, useRef, useState } from 'react'
import {
  Download,
  MessageSquare,
  RefreshCw,
  Sparkles,
  Upload,
  ImageIcon,
  Loader2,
} from 'lucide-react'
import { FeedbackModal } from '@/components/FeedbackModal'
import {
  downloadImage,
  fetchSoftware,
  generateImage,
  revokeBlobUrl,
  selectLevel,
  submitFeedback,
  type SoftwareInfo,
} from '@/lib/api'
import { cn, LEVEL_CONFIG } from '@/lib/utils'

/** 萝莉dao 桌面端主界面 */
function App() {
  const [software, setSoftware] = useState<SoftwareInfo | null>(null)
  const [selectedLevel, setSelectedLevel] = useState('L1')
  const [previewUrl, setPreviewUrl] = useState<string | null>(null)
  const [uploadFile, setUploadFile] = useState<File | null>(null)
  const [resultUrl, setResultUrl] = useState<string | null>(null)
  const [rawResultUrl, setRawResultUrl] = useState<string | null>(null)
  const [imageLoadError, setImageLoadError] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [message, setMessage] = useState('')
  const [feedbackText, setFeedbackText] = useState('')
  const [feedbackRating, setFeedbackRating] = useState<boolean | null>(null)
  const [showFeedback, setShowFeedback] = useState(false)
  const [submittingFeedback, setSubmittingFeedback] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    fetchSoftware().then(setSoftware).catch(() => {})
  }, [])

  /** 打开反馈弹窗 */
  const openFeedback = useCallback((presetRating?: boolean | null) => {
    if (presetRating !== undefined) setFeedbackRating(presetRating)
    setShowFeedback(true)
  }, [])

  /** 关闭反馈弹窗并重置表单 */
  const closeFeedback = useCallback(() => {
    setShowFeedback(false)
    setFeedbackText('')
    setFeedbackRating(null)
  }, [])

  /** 处理图片上传 */
  const handleUpload = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploadFile(file)
    setPreviewUrl(URL.createObjectURL(file))
    revokeBlobUrl(resultUrl)
    setResultUrl(null)
    setRawResultUrl(null)
    setImageLoadError(false)
    setMessage('')
  }, [resultUrl])

  useEffect(() => {
    return () => revokeBlobUrl(resultUrl)
  }, [resultUrl])

  /** 选择萝莉等级 */
  const handleSelectLevel = async (level: string) => {
    setSelectedLevel(level)
    try {
      await selectLevel(level)
    } catch {
      /* 静默失败 */
    }
  }

  /** 执行生图（首次生成或重新生成） */
  const runGenerate = async (isRegenerate = false) => {
    if (!uploadFile) {
      setMessage('请先上传兄弟的照片！（刷新页面后需重新上传）')
      return
    }
    setGenerating(true)
    setImageLoadError(false)
    const previousResultUrl = resultUrl
    const previousRawResultUrl = rawResultUrl
    if (isRegenerate) {
      revokeBlobUrl(resultUrl)
      setResultUrl(null)
      setRawResultUrl(null)
    }
    setMessage(isRegenerate ? '正在重新生成，姐妹再变一次~' : 'AI 正在施展魔法，兄弟即将变身...')
    try {
      const result = await generateImage(selectedLevel, uploadFile)
      revokeBlobUrl(previousResultUrl)
      setResultUrl(result.image_url)
      setRawResultUrl(result.raw_image_url)
      setMessage(result.message)
    } catch (e) {
      if (isRegenerate && previousResultUrl) {
        setResultUrl(previousResultUrl)
        setRawResultUrl(previousRawResultUrl)
      }
      const msg = e instanceof Error ? e.message : String(e)
      setMessage(`变身失败: ${msg}`)
    } finally {
      setGenerating(false)
    }
  }

  /** 首次生成时清空旧结果 */
  const handleGenerate = async () => {
    if (!uploadFile) {
      setMessage('请先上传兄弟的照片！')
      return
    }
    revokeBlobUrl(resultUrl)
    setResultUrl(null)
    setRawResultUrl(null)
    await runGenerate(false)
  }

  /** 重新生成（同一张照片、同一等级） */
  const handleRegenerate = () => runGenerate(true)

  /** 下载图片 */
  const handleDownload = async () => {
    if (!resultUrl) return
    const filename = `lolida_${selectedLevel}_${Date.now()}.png`
    try {
      const result = await downloadImage(resultUrl, filename)
      if (result.success) {
        setMessage('图片已保存！快发给兄弟看看~')
      }
    } catch {
      setMessage('保存失败，请重试')
    }
  }

  /** 提交用户反馈 */
  const handleSubmitFeedback = async () => {
    if (!feedbackText.trim()) {
      setMessage('请填写反馈内容~')
      return
    }
    setSubmittingFeedback(true)
    try {
      await submitFeedback({
        level: selectedLevel,
        is_valid: feedbackRating,
        content: feedbackText.trim(),
        image_path: rawResultUrl || resultUrl || '',
      })
      setMessage('反馈已提交，感谢兄弟的宝贵意见！🎀')
      closeFeedback()
    } catch (e) {
      const msg = e instanceof Error ? e.message : String(e)
      setMessage(`反馈提交失败: ${msg}`)
    } finally {
      setSubmittingFeedback(false)
    }
  }

  const levelInfo = LEVEL_CONFIG.find((l) => l.level === selectedLevel)

  return (
    <div className="min-h-screen p-4 md:p-6 pb-20">
      {/* 头部 */}
      <header className="text-center mb-6">
        <div className="inline-block animate-float text-6xl mb-2">🎀</div>
        <h1 className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-pink-500 to-purple-500 bg-clip-text text-transparent">
          {software?.name || '萝莉dao'}
        </h1>
        <p className="text-purple-500 mt-1 text-sm md:text-base animate-pulse">
          {software?.slogan || '今天的兄弟还会是兄弟吗？嘿嘿~'}
        </p>
      </header>

      <div className="max-w-4xl mx-auto grid md:grid-cols-2 gap-6">
        {/* 左侧：上传与等级选择 */}
        <div className="space-y-4">
          {/* 上传区域 */}
          <div
            className={cn(
              'border-3 border-dashed border-pink-300 rounded-2xl p-6 text-center cursor-pointer',
              'hover:border-pink-400 hover:bg-pink-50/50 transition-all',
              previewUrl && 'border-solid border-pink-400'
            )}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={handleUpload}
            />
            {previewUrl ? (
              <img src={previewUrl} alt="预览" className="max-h-48 mx-auto rounded-xl object-contain" />
            ) : (
              <div className="py-8">
                <Upload className="w-12 h-12 mx-auto text-pink-400 mb-3" />
                <p className="text-pink-600 font-bold">点击上传兄弟照片</p>
                <p className="text-xs text-gray-400 mt-1">支持 JPG、PNG，越帅效果越炸裂</p>
              </div>
            )}
          </div>

          {/* 等级选择 */}
          <div>
            <h3 className="text-sm font-bold text-pink-600 mb-2">选择萝莉等级</h3>
            <div className="grid grid-cols-5 gap-2">
              {LEVEL_CONFIG.map((l) => (
                <button
                  key={l.level}
                  onClick={() => handleSelectLevel(l.level)}
                  className={cn(
                    'flex flex-col items-center p-2 rounded-xl border-2 transition-all cursor-pointer',
                    selectedLevel === l.level
                      ? 'border-pink-500 bg-pink-100 level-btn-active'
                      : 'border-pink-200 bg-white hover:bg-pink-50'
                  )}
                >
                  <span className="text-xl">{l.emoji}</span>
                  <span className="text-xs font-bold text-pink-600">{l.level}</span>
                </button>
              ))}
            </div>
            {levelInfo && (
              <p className="text-xs text-purple-500 mt-2 text-center">
                {levelInfo.label} - {levelInfo.desc}
              </p>
            )}
          </div>

          {/* 变身按钮 */}
          <button
            onClick={handleGenerate}
            disabled={generating || !uploadFile}
            className={cn(
              'w-full py-4 rounded-2xl font-bold text-lg text-white transition-all cursor-pointer',
              'bg-gradient-to-r from-pink-500 to-purple-500',
              'hover:from-pink-600 hover:to-purple-600 hover:scale-[1.02]',
              'disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100',
              'animate-pulse-pink flex items-center justify-center gap-2'
            )}
          >
            {generating ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin-slow" /> 变身中...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" /> 一键变身
              </>
            )}
          </button>

          {message && (
            <p className={cn(
              'text-sm text-center p-3 rounded-xl',
              message.includes('失败') ? 'text-red-600 bg-red-50' : 'text-purple-600 bg-purple-50'
            )}>
              {message}
            </p>
          )}
          {message.includes('失败') && uploadFile && !generating && (
            <button
              onClick={() => runGenerate(true)}
              className="w-full py-2.5 rounded-xl border-2 border-pink-300 text-pink-600 font-bold hover:bg-pink-50 transition-all flex items-center justify-center gap-2 cursor-pointer"
            >
              <RefreshCw className="w-4 h-4" /> 重试
            </button>
          )}
        </div>

        {/* 右侧：结果展示 */}
        <div className="space-y-4">
          <div className="border-2 border-pink-200 rounded-2xl bg-white/70 backdrop-blur p-4 min-h-[320px] flex flex-col">
            <h3 className="text-sm font-bold text-pink-600 mb-3 flex items-center gap-2">
              <ImageIcon className="w-4 h-4" /> 变身结果
            </h3>

            {generating && (
              <div className="flex-1 flex flex-col items-center justify-center min-h-[240px] text-pink-400">
                <Loader2 className="w-10 h-10 animate-spin-slow mb-3" />
                <p className="text-sm font-bold">正在变身中，请稍候...</p>
              </div>
            )}

            {!generating && resultUrl && !imageLoadError && (
              <img
                src={resultUrl}
                alt="变身结果"
                className="w-full max-h-72 min-h-[180px] mx-auto rounded-xl object-contain bg-pink-50/50"
                onLoad={() => setImageLoadError(false)}
                onError={() => setImageLoadError(true)}
              />
            )}

            {!generating && imageLoadError && (
              <div className="flex-1 flex flex-col items-center justify-center min-h-[240px] text-red-400">
                <p className="text-sm font-bold">图片显示失败</p>
                {rawResultUrl && (
                  <a href={rawResultUrl} target="_blank" rel="noreferrer" className="text-xs text-purple-500 underline mt-2">
                    点击在新窗口查看
                  </a>
                )}
              </div>
            )}

            {!generating && !resultUrl && (
              <div className="flex-1 flex items-center justify-center text-gray-300 min-h-[240px]">
                <div className="text-center">
                  <span className="text-5xl">🪞</span>
                  <p className="mt-2 text-sm">变身结果将在这里显示</p>
                </div>
              </div>
            )}
          </div>

          {resultUrl && (
            <div className="flex flex-wrap gap-2">
              <button
                onClick={handleDownload}
                className="flex-1 py-2.5 px-4 rounded-xl bg-green-400 text-white font-bold hover:bg-green-500 transition-all flex items-center justify-center gap-2 cursor-pointer min-w-[120px]"
              >
                <Download className="w-4 h-4" /> 下载图片
              </button>
              <button
                onClick={handleRegenerate}
                disabled={generating || !uploadFile}
                className="flex-1 py-2.5 px-4 rounded-xl bg-pink-400 text-white font-bold hover:bg-pink-500 transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed min-w-[120px]"
              >
                <RefreshCw className={cn('w-4 h-4', generating && 'animate-spin-slow')} />
                重新生成
              </button>
              <button
                onClick={() => openFeedback(true)}
                className="py-2.5 px-4 rounded-xl bg-blue-400 text-white font-bold hover:bg-blue-500 transition-all cursor-pointer text-sm"
              >
                👍 有效
              </button>
              <button
                onClick={() => openFeedback(false)}
                className="py-2.5 px-4 rounded-xl bg-orange-400 text-white font-bold hover:bg-orange-500 transition-all cursor-pointer text-sm"
              >
                👎 无效
              </button>
            </div>
          )}

        </div>
      </div>

      {/* 右下角悬浮反馈按钮 */}
      <button
        onClick={() => openFeedback()}
        className={cn(
          'fixed bottom-6 right-6 z-40 flex items-center gap-2',
          'px-5 py-3 rounded-full font-bold text-white shadow-lg',
          'bg-gradient-to-r from-purple-500 to-pink-500',
          'hover:from-purple-600 hover:to-pink-600 hover:scale-105',
          'transition-all cursor-pointer animate-bounce-fun'
        )}
      >
        <MessageSquare className="w-5 h-5" />
        意见反馈
      </button>

      <FeedbackModal
        open={showFeedback}
        onClose={closeFeedback}
        selectedLevel={selectedLevel}
        onLevelChange={setSelectedLevel}
        feedbackText={feedbackText}
        onFeedbackTextChange={setFeedbackText}
        feedbackRating={feedbackRating}
        onFeedbackRatingChange={setFeedbackRating}
        onSubmit={handleSubmitFeedback}
        submitting={submittingFeedback}
        hasResult={!!resultUrl}
      />
    </div>
  )
}

export default App
