import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/** 合并 Tailwind 类名 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

/** 等级配置 */
export const LEVEL_CONFIG = [
  { level: 'L1', label: '萌新萝莉', emoji: '🌸', color: 'from-green-300 to-green-400', desc: '轻度美颜，兄弟还能认得出' },
  { level: 'L2', label: '可爱加倍', emoji: '🎀', color: 'from-blue-300 to-blue-400', desc: '双马尾觉醒，杀伤力+1' },
  { level: 'L3', label: '萌系觉醒', emoji: '💖', color: 'from-purple-300 to-purple-400', desc: '洛丽塔初现，群聊必备' },
  { level: 'L4', label: '魅力全开', emoji: '✨', color: 'from-pink-300 to-pink-400', desc: '萝莉公主，可爱拉满' },
  { level: 'L5', label: '终极变身', emoji: '👑', color: 'from-red-300 to-red-400', desc: '友谊的小船说翻就翻' },
] as const
