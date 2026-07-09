import { useState } from 'react'
import { Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { adminLogin, setToken } from '@/lib/api'

interface LoginPageProps {
  onLogin: () => void
  initialError?: string
}

/** 管理员登录页 */
export function LoginPage({ onLogin, initialError = '' }: LoginPageProps) {
  const [password, setPassword] = useState('')
  const [error, setError] = useState(initialError)
  const [loading, setLoading] = useState(false)

  /** 提交登录表单 */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const result = await adminLogin(password)
      if (result.success) {
        setToken(result.token)
        onLogin()
      } else {
        setError('密码错误，兄弟你是不是卧底？')
      }
    } catch {
      setError('登录失败，请确认后端 server 已启动')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center p-4">
      <Card className="w-full max-w-md animate-bounce-fun">
        <CardHeader className="text-center">
          <div className="mx-auto mb-2 text-5xl">👑</div>
          <CardTitle className="text-2xl">萝莉dao 管理后台</CardTitle>
          <p className="text-sm text-purple-500 mt-1">今天的兄弟还会是兄弟吗？嘿嘿~</p>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              type="password"
              placeholder="输入管理员密码"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            {error && <p className="text-red-500 text-sm text-center">{error}</p>}
            <Button type="submit" className="w-full" disabled={loading}>
              <Sparkles className="w-4 h-4" />
              {loading ? '验证中...' : '进入后台'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
