import { useState } from "react";
import CheckEmailStep      from "../components/auth/CheckEmailStep";
import VerifyOTPStep       from "../components/auth/VerifyOTPStep";
import LoginStep           from "../components/auth/LoginStep";
import CompleteProfileStep from "../components/auth/CompleteProfileStep";

/**
 * AuthPage — master controller for the entire auth flow
 *
 * Flow:
 *   email → "login"      → LoginStep      → onDone()
 *   email → "signup"     → VerifyOTPStep  → CompleteProfileStep → onDone()
 *   email → "verify_otp" → VerifyOTPStep  → CompleteProfileStep → onDone()
 *   login → "forgot"     → VerifyOTPStep (password_reset) → onDone()
 */
export default function AuthPage({ onDone }) {
  const [step, setStep]   = useState("email");
  const [state, setState] = useState({
    email:   "",
    tokens:  null,
    otpType: "signup",
  });

  const update = (patch) => setState((s) => ({ ...s, ...patch }));

  // ── STEP 1: Check Email ────────────────────────────────
  if (step === "email") {
    return (
      <CheckEmailStep
        onNext={({ email, flow }) => {
          update({ email });
          if (flow === "login") {
            setStep("login");
          } else {
            // "signup" or "verify_otp" both go to OTP screen
            update({ otpType: "signup" });
            setStep("otp");
          }
        }}
      />
    );
  }

  // ── STEP 2A: Verify OTP (signup / password reset) ─────
  if (step === "otp") {
    return (
      <VerifyOTPStep
        email={state.email}
        otpType={state.otpType}
        onBack={() => setStep("email")}
        onNext={({ tokens }) => {
          update({ tokens });
          setStep("profile");
        }}
      />
    );
  }

  // ── STEP 2B: Login (existing verified user) ───────────
  if (step === "login") {
    return (
      <LoginStep
        email={state.email}
        onSuccess={onDone}
        onBack={(action) => {
          if (action === "forgot") {
            // Forgot password → send OTP for password_reset
            update({ otpType: "password_reset" });
            setStep("otp");
          } else {
            setStep("email");
          }
        }}
      />
    );
  }

  // ── STEP 3: Complete Profile (after OTP verify) ───────
  if (step === "profile") {
    return (
      <CompleteProfileStep
        tokens={state.tokens}
        onSuccess={onDone}
      />
    );
  }

  return null;
}
