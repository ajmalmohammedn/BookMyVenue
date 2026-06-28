import Logo from "../ui/Logo";


export default function AuthLayout({ children, step, total }) {
  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <div className="flex items-center justify-between px-6 py-4">
        <Logo />
        {step && (
          <div className="flex items-center gap-2">
            {Array.from({ length: total }).map((_, i) => (
              <div
                key={i}
                className={`h-1.5 rounded-full transition-all duration-300
                  ${i < step ? "w-8 bg-amber-500" : "w-4 bg-slate-200"}`}
              />
            ))}
          </div>
        )}
      </div>

      <div className="flex-1 flex items-center justify-center px-4 py-12">
        <div className="w-full max-w-sm">{children}</div>
      </div>

      <p className="text-center text-xs text-slate-400 pb-6">
        © 2025 BookMyVenue · All rights reserved
      </p>
    </div>
  );
}
