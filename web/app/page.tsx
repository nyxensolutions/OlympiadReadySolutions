import { SignedIn, SignedOut, SignInButton, SignUpButton } from "@clerk/nextjs";
import { AppHeader } from "@/components/AppHeader";
import { GeneratorFlow } from "@/components/GeneratorFlow";

export default function Home() {
  return (
    <main className="mx-auto flex min-h-screen max-w-5xl flex-col items-center px-4 py-10 sm:py-16">
      <AppHeader active="home" />

      <section className="mt-12 flex flex-col items-center text-center sm:mt-16">
        <h1 className="max-w-3xl text-3xl font-bold tracking-tight text-slate-900 sm:text-5xl">
          AI-generated Olympiad practice papers,
          <br />
          tailored to your class and level.
        </h1>
        <p className="mt-4 max-w-xl text-base text-slate-600 sm:text-lg">
          SOF · SilverZone style questions for Math, Science, English, and Cyber.
          Generate a paper, attempt it with a timer, and download the PDF.
        </p>
      </section>

      <section className="mt-10 flex w-full justify-center">
        <SignedIn>
          <GeneratorFlow />
        </SignedIn>
        <SignedOut>
          <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
            <h2 className="text-lg font-semibold text-slate-900">Sign in to start</h2>
            <p className="mt-2 text-sm text-slate-600">
              Sign up free to generate practice papers, take timed tests, and download
              PDFs of every paper you create.
            </p>
            <div className="mt-5 flex justify-center gap-2">
              <SignInButton mode="modal">
                <button className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50">
                  Sign in
                </button>
              </SignInButton>
              <SignUpButton mode="modal">
                <button className="rounded-lg bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700">
                  Create free account
                </button>
              </SignUpButton>
            </div>
          </div>
        </SignedOut>
      </section>

      <footer className="mt-16 text-xs text-slate-400">
        Prototype · auth via Clerk · billing via Razorpay
      </footer>
    </main>
  );
}
