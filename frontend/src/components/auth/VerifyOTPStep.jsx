import { useState, useEffect } from "react";
import { verifyOTP, resendOTP } from "../../api/auth";
import AuthLayout from "./AuthLayout";
import { Button, Card, Alert } from "../ui";

export default function VerifyOTPStep({ email, otpType = "signup", onNext, onBack }) {
  const [otp, setOtp]             = useState(["", "", "", "", "", ""]);
  const [error, setError]         = useState("");
  const [resendMsg, setResendMsg] = useState("");
  const [loading, setLoading]     = useState(false);
  const [countdown, setCountdown] = useState(60);
  const [canResend, setCanResend] = useState(false);

  useEffect(() => {
    if (countdown <= 0) { setCanResend(true); return; }
    const t = setTimeout(() => setCountdown((c) => c - 1), 1000);
    return () => clearTimeout(t);
  }, [countdown]);

  const handleChange = (val, idx) => {
    if (!/^\d?$/.test(val)) return;
    const next = [...otp];
    next[idx] = val;
    setOtp(next);
    if (val && idx < 5) document.getElementById(`otp-${idx + 1}`)?.focus();
  };

  const handleKeyDown = (e, idx) => {
    if (e.key === "Backspace" && !otp[idx] && idx > 0)
      document.getElementById(`otp-${idx - 1}`)?.focus();
  };

  const handleSubmit = async () => {
    const code = otp.join("");
    if (code.length < 6) return setError("Please enter the 6-digit OTP.");
    setError("");
    setLoading(true);
    try {
      const { data } = await verifyOTP(email, code, otpType);
      onNext({ tokens: data.tokens });
    } catch (err) {
      setError(err.response?.data?.error || "Invalid OTP.");
    } finally {
      setLoading(false);
    }
  };

  const handleResend = async () => {
    setResendMsg("");
    setError("");
    try {
      await resendOTP(email);
      setResendMsg("New OTP sent!");
      setCountdown(60);
      setCanResend(false);
    } catch (err) {
      setError(err.response?.data?.error || "Could not resend OTP.");
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
            Verification
          </p>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Check your email</h1>
          <p className="text-slate-500 text-sm mt-2">
            We sent a 6-digit code to{" "}
            <span className="font-medium text-slate-700">{email}</span>
          </p>
        </div>

        <Card className="p-6 space-y-5">
          {/* OTP boxes */}
          <div className="flex gap-2 justify-between">
            {otp.map((digit, i) => (
              <input
                key={i}
                id={`otp-${i}`}
                type="text"
                inputMode="numeric"
                maxLength={1}
                value={digit}
                onChange={(e) => handleChange(e.target.value, i)}
                onKeyDown={(e) => handleKeyDown(e, i)}
                className={`w-11 h-12 text-center text-lg font-bold rounded-xl border outline-none
                  transition-all duration-150 focus:ring-2 focus:ring-amber-400 focus:border-amber-400
                  ${digit
                    ? "border-amber-400 bg-amber-50 text-amber-700"
                    : "border-slate-200 text-slate-900"
                  }`}
              />
            ))}
          </div>

          {error    && <Alert type="error"   message={error} />}
          {resendMsg && <Alert type="success" message={resendMsg} />}

          <Button loading={loading} onClick={handleSubmit} className="w-full">
            Verify code
          </Button>

          <div className="text-center">
            {canResend ? (
              <button
                onClick={handleResend}
                className="text-sm text-amber-600 hover:text-amber-700 font-medium"
              >
                Resend code
              </button>
            ) : (
              <p className="text-sm text-slate-400">
                Resend in{" "}
                <span className="font-medium text-slate-600">{countdown}s</span>
              </p>
            )}
          </div>
        </Card>
      </div>
    </AuthLayout>
  );
}
