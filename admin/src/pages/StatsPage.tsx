import { useEffect, useState } from 'react'
import { BarChart3 } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { type LevelStat, fetchStats } from '@/lib/api'

const LEVEL_COLORS: Record<string, string> = {
  L1: 'bg-green-400',
  L2: 'bg-blue-400',
  L3: 'bg-purple-400',
  L4: 'bg-pink-400',
  L5: 'bg-red-400',
}

/** 等级统计页 */
export function StatsPage() {
  const [stats, setStats] = useState<LevelStat[]>([])

  useEffect(() => {
    fetchStats().then(setStats)
  }, [])

  const maxSelect = Math.max(...stats.map((s) => s.select_count), 1)
  const maxGenerate = Math.max(...stats.map((s) => s.generate_count), 1)

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold text-pink-600 flex items-center gap-2">
        <BarChart3 className="w-6 h-6" /> 等级统计
      </h2>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {stats.map((s) => (
          <Card key={s.level}>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <span className={`w-8 h-8 rounded-full ${LEVEL_COLORS[s.level]} flex items-center justify-center text-white text-sm`}>
                  {s.level}
                </span>
                {s.label}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>选择次数</span>
                  <span className="font-bold text-pink-600">{s.select_count}</span>
                </div>
                <div className="h-3 bg-pink-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-pink-400 rounded-full transition-all"
                    style={{ width: `${(s.select_count / maxSelect) * 100}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span>生成次数</span>
                  <span className="font-bold text-purple-600">{s.generate_count}</span>
                </div>
                <div className="h-3 bg-purple-100 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-purple-400 rounded-full transition-all"
                    style={{ width: `${(s.generate_count / maxGenerate) * 100}%` }}
                  />
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  )
}
