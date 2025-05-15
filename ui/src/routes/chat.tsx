import Chat from '@/components/owned/Chat'
import { Button } from '@/components/ui/button'
import { createFileRoute, Link } from '@tanstack/react-router'
import { ChevronLeftIcon } from 'lucide-react'

export const Route = createFileRoute('/chat')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div className="bg-none relative px-4 py-2 flex items-end justify-center w-svw h-svh">
    <Link to={'/'}>
      <Button variant='link' className='absolute top-4 left-0 text-center' >
        <ChevronLeftIcon /> Back
      </Button>
    </Link>
    <Chat />
  </div>
}
