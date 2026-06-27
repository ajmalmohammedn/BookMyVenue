export default function Alert({ type = "error", message }) {
  if (!message) return null;
  const styles = {
    error:   "bg-red-50 border-red-200 text-red-700",
    success: "bg-green-50 border-green-200 text-green-700",
    info:    "bg-amber-50 border-amber-200 text-amber-700",
  };
  return (
    <div className={`px-4 py-3 rounded-xl border text-sm ${styles[type]}`}>
      {message}
    </div>
  );
}
