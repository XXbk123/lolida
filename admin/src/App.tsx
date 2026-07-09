import { useEffect, useState } from 'react'
import { LogOut, MessageSquare, BarChart3, FileText } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { AuthError, clearToken, getToken } from '@/lib/api'
import { LoginPage } from '@/pages/LoginPage'
import { SchemesPage } from '@/pages/SchemesPage'
import { FeedbackPage } from '@/pages/FeedbackPage'
import { StatsPage } from '@/pages/StatsPage'

type Tab = 'schemes' | 'feedback' | 'stats'

/** 管理后台主应用 */
function App() {
  const [authed, setAuthed] = useState(!!getToken())
  const [tab, setTab] = useState<Tab>('schemes')
  const [authError, setAuthError] = useState('')

  /** 退出登录 */
  const handleLogout = () => {
    clearToken()
    setAuthed(false)
    setAuthError('')
  }

  /** 监听子页面认证失败 */
  const handleAuthError = (err: unknown) => {
    if (err instanceof AuthError) {
      setAuthed(false)
      setAuthError(err.message)
    }
  }

  if (!authed) {
    return <LoginPage onLogin={() => { setAuthed(true); setAuthError('') }} initialError={authError} />
  }

  const tabs: { id: Tab; label: string; icon: React.ReactNode }[] = [
    { id: 'schemes', label: '方案管理', icon: <FileText className="w-4 h-4" /> },
    { id: 'feedback', label: '用户反馈', icon: <MessageSquare className="w-4 h-4" /> },
    { id: 'stats', label: '数据统计', icon: <BarChart3 className="w-4 h-4" /> },
  ]

  return (
    <div className="min-h-screen">
      <header className="border-b-2 border-pink-200 bg-white/70 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-3xl animate-wiggle">🎀</span>
            <div>
              <h1 className="text-xl font-bold text-pink-600">萝莉dao 管理后台</h1>
              <p className="text-xs text-purple-500">今天的兄弟还会是兄弟吗？嘿嘿~</p>
            </div>
          </div>
          <Button variant="ghost" size="sm" onClick={handleLogout}>
            <LogOut className="w-4 h-4" /> 退出
          </Button>
        </div>
      </header>

      <nav className="max-w-6xl mx-auto px-4 py-3 flex gap-2">
        {tabs.map((t) => (
          <Button
            key={t.id}
            variant={tab === t.id ? 'default' : 'outline'}
            size="sm"
            onClick={() => setTab(t.id)}
          >
            {t.icon} {t.label}
          </Button>
        ))}
      </nav>

      <main className="max-w-6xl mx-auto px-4 pb-8">
        {tab === 'schemes' && <SchemesPage onAuthError={handleAuthError} />}
        {tab === 'feedback' && <FeedbackPage onAuthError={handleAuthError} />}
        {tab === 'stats' && <StatsPage />}
      </main>
    </div>
  )
}

export default App
