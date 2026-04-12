'use client'

import { useEffect } from 'react'
import { Button } from '@/components/ui/button'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('App Error:', error)
  }, [error])

  return (
    <div className='flex flex-col items-center justify-center min-h-[60vh] gap-6 p-8'>
      <div className='border-4 border-red-500 p-8 max-w-lg w-full text-center'>
        <h2 className='text-2xl font-black uppercase tracking-tight text-black dark:text-white mb-2'>
          Something went wrong
        </h2>
        <p className='text-sm font-medium text-gray-500 dark:text-gray-400 mb-6'>
          We hit an unexpected error. Please try again.
        </p>
        <Button
          onClick={() => reset()}
          className='rounded-none bg-black dark:bg-white text-white dark:text-black font-black uppercase border-2 border-black dark:border-white px-8 py-3 hover:translate-x-[2px] hover:translate-y-[2px] transition-all shadow-[4px_4px_0px_0px_rgba(0,0,0,1)]'
        >
          Try Again
        </Button>
      </div>
    </div>
  )
}
