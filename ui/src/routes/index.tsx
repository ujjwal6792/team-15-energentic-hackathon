import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { createFileRoute } from '@tanstack/react-router'
import { Link } from '@tanstack/react-router'

export const Route = createFileRoute("/")({
  component: HomePage,
})

function HomePage() {
  return (
    <div className="bg-none py-12 px-6 w-svw h-svh min-h-screen text-gray-900 md:px-20 lg:px-32 overflow-scroll">
      <header className="text-center max-w-3xl mx-auto text-[#4c4f69]">
        <h1 className="text-4xl font-bold tracking-tight lg:text-5xl">
          Welcome to Smarter Solarization
        </h1>
        <p className="mt-4 text-lg text-[#5c5f77]">
          Clean Energy. Full Control. Grid-Ready from Day One.
        </p>
      </header>

      <section className=" max-w-5xl mx-auto mt-12 flex overflow-scroll scroll-smooth lg:grid gap-6 lg:grid-cols-2">
        <Card className='min-w-64 border-none bg-[#F9F5DD]/40 text-[#7287fd]'>
          <CardContent className="p-6">
            <h2 className="text-xl font-semibold">Local Eligibility Checked Instantly</h2>
            <p className="mt-2 text-[#4c4f69]">
              From roof geometry to rebate programs, we run the numbers so you don’t have to.
            </p>
          </CardContent>
        </Card>
        <Card className='min-w-64 border-none bg-[#F9F5DD]/40 text-[#7287fd]'>
          <CardContent className="p-6">
            <h2 className="text-xl font-semibold">Free Site Survey Scheduled</h2>
            <p className="mt-2 text-[#4c4f69]">
              Top-rated local installers. Certified. No spam calls.
            </p>
          </CardContent>
        </Card>
        <Card className='min-w-64 border-none bg-[#F9F5DD]/40 text-[#7287fd]'>
          <CardContent className="p-6">
            <h2 className="text-xl font-semibold">Automatic Subsidy Applications</h2>
            <p className="mt-2 text-[#4c4f69]">
              Federal and state incentives fast-tracked. Typical savings: <strong>up to $6,000</strong>.
            </p>
          </CardContent>
        </Card>
      </section>

      <section className="mt-20 text-center">
        <h2 className="text-3xl font-bold mb-4 text-[#4c4f69]">Ready to Get Started?</h2>
        <p className="text-lg  mb-6 text-[#5c5f77]">
          No forms. No calls. Just a guided experience.
        </p>
        <Link className='w-full flex justify-center' to='/chat'>
          {/* <button className='bg-primary/50 text-foreground px-2 py-4 rounded cursor-pointer backdrop-blur-md'>Let's Begin</button> */}
          <Button type="button" className="text-white text-xl bg-gradient-to-br from-[#7287fd] to-[#7287fd80] 
        hover:bg-gradient-to-bl focus:ring-4 focus:outline-none focus:ring-blue-300 dark:focus:ring-blue-800 
        font-medium rounded-lg px-10 py-6 text-center me-2 mb-2 transition-colors duration-500">
            Let's Begin
          </Button>
        </Link>
      </section>

      <section className="mt-16 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold mb-4">How It Works</h2>
        <ul className="space-y-4">
          <li>
            <strong>Step 1:</strong> You Say "Go" — nothing moves without your consent.
          </li>
          <li>
            <strong>Step 2:</strong> Site Survey & Custom Plan — we generate battery-ready system designs.
          </li>
          <li>
            <strong>Step 3:</strong> Install, Permit & Interconnect — we handle every detail.
          </li>
          <li>
            <strong>Step 4:</strong> Activate Your Power — register, enable net metering, and optional grid rewards.
          </li>
        </ul>
      </section>

      <section className="mt-16 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold mb-4">Add a Battery. Unlock More.</h2>
        <p className=" mb-2">Include backup power to:</p>
        <ul className="list-disc list-inside">
          <li>Stay resilient during outages ⚡</li>
          <li>Earn rewards in grid events 💵</li>
          <li>Enable peak-load flexibility and future smart incentives</li>
        </ul>
      </section>

      <section className="mt-16 max-w-4xl mx-auto">
        <h2 className="text-2xl font-bold mb-4">You're In Control, Always</h2>
        <p className=" mb-4">
          You’ll receive:
        </p>
        <ul className="list-disc list-inside ">
          <li>A live dashboard to track installs, permits, and savings</li>
          <li>Participation options with manual opt-in only</li>
          <li>Major update notifications (or weekly check-ins—your choice)</li>
        </ul>
      </section>

    </div>
  )
}
