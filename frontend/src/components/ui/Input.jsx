export default function Input({ label, error, ...props }) {
  return (
    <div className="flex flex-col gap-1.5">
      {label && (
        <label className="text-sm font-medium text-slate-700">{label}</label>
      )}
      <input
        {...props}
        className={`w-full px-4 py-3 rounded-xl border text-slate-900 text-sm bg-white
          placeholder-slate-400 outline-none transition-all duration-150
          focus:ring-2 focus:ring-amber-400 focus:border-amber-400
          ${error
            ? "border-red-400 bg-red-50"
            : "border-slate-200 hover:border-slate-300"
          }`}
      />
      {error && <p className="text-xs text-red-500">{error}</p>}
    </div>
  );
}
