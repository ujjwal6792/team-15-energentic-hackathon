import Chat from '@/components/owned/Chat'
import { Button } from '@/components/ui/button'
import { useSessionStore } from '@/store'
import { createFileRoute, Link } from '@tanstack/react-router'
import { ChevronLeftIcon } from 'lucide-react'
import { useEffect } from 'react'

export const Route = createFileRoute('/chat')({
  component: RouteComponent,
})

function RouteComponent() {
  const { createSession, session, loading, error } = useSessionStore()

  useEffect(() => {
    createSession()
  }, [])

  if (loading || !session) return <p>Creating session...</p>
  if (error) return <p>Error: {error}</p>

  return <div className="bg-none relative px-4 py-2 flex items-end justify-center w-full h-dvh">
    <Link to={'/'}>
      <Button variant='link' className='absolute top-4 left-0 text-center' >
        <ChevronLeftIcon /> Back
      </Button>
    </Link>
    <Chat session={session} />
  </div>
}
