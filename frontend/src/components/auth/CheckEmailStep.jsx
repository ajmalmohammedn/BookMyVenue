import { useState } from "react";
import { checkEmail } from "../../api/auth";
import AuthLayout from "./AuthLayout";
import { Button, Input,Card} from '../ui'

export default function CheckEmailStep({ onNext }) {
  const [email, setEmail]     = useState("");
  const [error, setError]     = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!email.trim()) return setError("Please enter your email.");
    setError("");
    setLoading(true);
    try {
      const { data } = await checkEmail(email.toLowerCase().trim());
      onNext({ email: email.toLowerCase().trim(), flow: data.status });
    } catch (err) {
      setError(err.response?.data?.email?.[0] || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout step={1} total={3}>
      <div className="space-y-6">
        <div>
          <p className="text-xs font-semibold text-amber-500 tracking-widest uppercase mb-2">
            Welcome
          </p>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">
            Find or book your perfect venue
          </h1>
          <p className="text-slate-500 text-sm mt-2">Enter your email to get started.</p>
        </div>

        <Card className="p-6 space-y-4">
          <Input
            label="Email address"
            type="email"
            placeholder="you@example.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
            error={error}
            autoFocus
          />
          <Button loading={loading} onClick={handleSubmit} className="w-full">
            Continue →
          </Button>
        </Card>

        <p className="text-center text-xs text-slate-400">
          By continuing, you agree to our{" "}
          <span className="text-slate-600 underline cursor-pointer">Terms</span> and{" "}
          <span className="text-slate-600 underline cursor-pointer">Privacy Policy</span>.
        </p>
      </div>
    </AuthLayout>
  );
}
