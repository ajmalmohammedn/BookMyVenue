export default function Logo() {
  return (
    <div className="flex items-center gap-2">
      <div className="w-8 h-8 bg-amber-500 rounded-lg flex items-center justify-center">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="white">
          <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
          <polyline
            points="9 22 9 12 15 12 15 22"
            fill="none"
            stroke="white"
            strokeWidth="2"
          />
        </svg>
      </div>
      <span className="font-bold text-slate-900 tracking-tight">BookMyVenue</span>
    </div>
  );
}
