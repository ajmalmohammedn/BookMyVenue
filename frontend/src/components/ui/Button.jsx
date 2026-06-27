export default function Button({
  children, loading, variant = "primary", className = "", ...props
}) {
  const base = "inline-flex items-center justify-center gap-2 px-6 py-3 rounded-xl font-semibold text-sm transition-all duration-150 disabled:opacity-60 disabled:cursor-not-allowed cursor-pointer";
  const variants = {
    primary: "bg-amber-500 hover:bg-amber-600 active:scale-95 text-white shadow-sm",
    outline: "border-2 border-slate-200 hover:border-slate-300 text-slate-700 bg-white hover:bg-slate-50",
    ghost:   "text-slate-600 hover:text-slate-900 hover:bg-slate-100",
    danger:  "bg-rose-600 hover:bg-rose-700 text-white",
  };
  return (
    <button
      {...props}
      disabled={loading || props.disabled}
      className={`${base} ${variants[variant] || variants.primary} ${className}`}
    >
      {loading ? <Spinner /> : children}
    </button>
  );
}

function Spinner() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" className="animate-spin">
      <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="3"
        strokeDasharray="40" strokeDashoffset="10" />
    </svg>
  );
}
