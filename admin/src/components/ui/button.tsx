import * as React from 'react'
import { Slot } from '@radix-ui/react-slot'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center gap-2 rounded-xl font-bold transition-all duration-200 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed',
  {
    variants: {
      variant: {
        default: 'bg-pink-500 text-white hover:bg-pink-600 hover:scale-105 shadow-lg shadow-pink-200',
        secondary: 'bg-purple-400 text-white hover:bg-purple-500 hover:scale-105',
        outline: 'border-2 border-pink-400 text-pink-600 hover:bg-pink-50',
        danger: 'bg-red-400 text-white hover:bg-red-500',
        ghost: 'text-pink-600 hover:bg-pink-100',
      },
      size: {
        default: 'px-5 py-2.5 text-sm',
        sm: 'px-3 py-1.5 text-xs',
        lg: 'px-8 py-3 text-base',
      },
    },
    defaultVariants: { variant: 'default', size: 'default' },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

/** 活泼风格按钮组件 */
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    const Comp = asChild ? Slot : 'button'
    return <Comp className={cn(buttonVariants({ variant, size, className }))} ref={ref} {...props} />
  }
)
Button.displayName = 'Button'

export { Button, buttonVariants }
