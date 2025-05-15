import Chat from '@/components/owned/Chat'
import { Button } from '@/components/ui/button'
import { createFileRoute } from '@tanstack/react-router'
import { ChevronLeftIcon } from 'lucide-react'

export const Route = createFileRoute('/chat')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div className="bg-[url('./solar-bg.svg')] relative px-4 py-2 flex items-end justify-center bg-cover bg-center w-svw h-svh">
    <Button variant='link' className='absolute top-4 left-0 text-center' >
      <ChevronLeftIcon /> Back
    </Button>
    <Chat />
  </div>
}
