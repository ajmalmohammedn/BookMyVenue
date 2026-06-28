import { useAuth } from "../context/AuthContext";
import { Logo, Button } from "../components/ui";

export default function HomePage({ onGetStarted }) {
  const { user, doLogout } = useAuth();

  return (
    <div className="min-h-screen bg-white font-sans">
      {/* Nav */}
      <nav className="sticky top-0 z-50 bg-white/90 backdrop-blur border-b border-slate-100">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Logo />
          <div className="flex items-center gap-3">
            {user ? (
              <>
                <span className="text-sm text-slate-600 hidden md:block">
                  Hi, {user.full_name?.split(" ")[0] || "there"} 👋
                </span>
                <Button variant="outline" onClick={doLogout} className="text-xs px-4 py-2">
                  Sign out
                </Button>
              </>
            ) : (
              <>
                <Button variant="ghost" onClick={onGetStarted} className="text-sm px-4 py-2">
                  Sign in
                </Button>
                <Button onClick={onGetStarted} className="text-sm px-4 py-2">
                  Get started
                </Button>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-6xl mx-auto px-6 pt-20 pb-16">
        <div className="max-w-2xl">
          <div className="inline-flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-full px-4 py-1.5 mb-6">
            <span className="w-2 h-2 bg-amber-500 rounded-full animate-pulse" />
            <span className="text-xs font-semibold text-amber-700">3,200+ venues ready to book</span>
          </div>

          <h1 className="text-5xl md:text-6xl font-extrabold text-slate-900 leading-[1.05] tracking-tight mb-6">
            Every event deserves the{" "}
            <span className="relative">
              <span className="relative z-10 text-amber-500">right venue</span>
              <span className="absolute bottom-1 left-0 right-0 h-3 bg-amber-100 -z-0 rounded" />
            </span>
          </h1>

          <p className="text-lg text-slate-500 leading-relaxed mb-8 max-w-lg">
            Search, compare, and book venues for weddings, corporate events, birthdays and more.
          </p>

          <div className="flex gap-2 p-2 bg-white border border-slate-200 rounded-2xl shadow-sm max-w-lg">
            <input
              placeholder="Search by city or venue name…"
              className="flex-1 px-4 py-2 text-sm text-slate-900 placeholder-slate-400 outline-none bg-transparent"
            />
            <Button onClick={onGetStarted} className="shrink-0">
              Search venues
            </Button>
          </div>
        </div>
      </section>

      {/* CTA Banner */}
      <section className="py-16">
        <div className="max-w-6xl mx-auto px-6">
          <div className="bg-slate-900 rounded-3xl px-8 py-14 text-center relative overflow-hidden">
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="w-96 h-48 bg-amber-500 opacity-10 rounded-full blur-3xl" />
            </div>
            <div className="relative z-10">
              <p className="text-xs font-semibold text-amber-400 tracking-widest uppercase mb-3">
                Own a venue?
              </p>
              <h2 className="text-3xl font-extrabold text-white tracking-tight mb-4">
                List your venue and reach thousands of customers
              </h2>
              <Button
                onClick={onGetStarted}
                className="bg-amber-500 hover:bg-amber-400 text-white px-8 py-3 text-base"
              >
                List your venue for free →
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-100 py-10">
        <div className="max-w-6xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
          <Logo />
          <p className="text-xs text-slate-400">© 2025 BookMyVenue · Built for India's event industry</p>
          <div className="flex gap-6 text-xs text-slate-400">
            <span className="cursor-pointer hover:text-slate-600">Privacy</span>
            <span className="cursor-pointer hover:text-slate-600">Terms</span>
            <span className="cursor-pointer hover:text-slate-600">Contact</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
