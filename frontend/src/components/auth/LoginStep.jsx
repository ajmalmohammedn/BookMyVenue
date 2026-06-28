import { useState } from "react";
import { login } from "../../api/auth";
import { useAuth } from "../../context/AuthContext";
import AuthLayout from "./AuthLayout";
import { Button, Input, Card } from "../ui";

export default function LoginStep({ email, onSuccess, onBack }) {
  const { saveLogin }             = useAuth();
  const [password, setPassword]   = useState("");
  const [showPass, setShowPass]   = useState(false);
  const [error, setError]         = useState("");
  const [loading, setLoading]     = useState(false);

  const handleSubmit = async () => {
    if (!password) return setError("Please enter your password.");
    setError("");
    setLoading(true);
    try {
      const { data } = await login(email, password);
      saveLogin(data.user, data.token);
      onSuccess();
    } catch (err) {
      setError(err.response?.data?.error || "Login failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout step={2} total={3}>
      <div className="space-y-6">
        <div>
          <button
            onClick={onBack}
            className="text-slate-400 hover:text-slate-600 text-sm mb-4 flex items-center gap-1"
          >
            ← Back
          </button>
          <p className="text-xs font-semibold text-amber-500 tracking-widest uppercase mb-2">
            Welcome back
          </p>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Enter your password</h1>
          <p className="text-slate-500 text-sm mt-2">
            Signing in as{" "}
            <span className="font-medium text-slate-700">{email}</span>
          </p>
        </div>

        <Card className="p-6 space-y-4">
          <div className="relative">
            <Input
              label="Password"
              type={showPass ? "text" : "password"}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
              error={error}
              autoFocus
            />
            <button
              type="button"
              onClick={() => setShowPass((s) => !s)}
              className="absolute right-3 top-9 text-slate-400 hover:text-slate-600 text-xs"
            >
              {showPass ? "Hide" : "Show"}
            </button>
          </div>

          <Button loading={loading} onClick={handleSubmit} className="w-full">
            Sign in
          </Button>

          <div className="text-center">
            <button
              onClick={() => onBack("forgot")}
              className="text-sm text-amber-600 hover:text-amber-700 font-medium"
            >
              Forgot password?
            </button>
          </div>
        </Card>
      </div>
    </AuthLayout>
  );
}
