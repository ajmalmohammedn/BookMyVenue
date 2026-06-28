import { useState } from "react";
import { completeProfile, setPassword } from "../../api/auth";
import { useAuth } from "../../context/AuthContext";
import AuthLayout from "./AuthLayout";
import { Button, Input, Card, Alert } from "../ui";

const ROLES = [
  { value: "customer",    label: "I want to book venues", icon: "🎉" },
  { value: "venue_owner", label: "I own a venue to list", icon: "🏢" },
];

export default function CompleteProfileStep({ tokens, onSuccess }) {
  const { saveLogin } = useAuth();

  const [form, setForm] = useState({
    full_name: "", phone_number: "+91", city: "",
    state: "", role: "customer", password: "", confirm_password: "",
  });
  const [errors, setErrors]   = useState({});
  const [alert, setAlert]     = useState("");
  const [loading, setLoading] = useState(false);

  const upd = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const validate = () => {
    const e = {};
    if (!form.full_name || form.full_name.trim().length < 3)
      e.full_name = "At least 3 characters.";
    if (!form.phone_number.startsWith("+"))
      e.phone_number = "Must start with + (e.g. +919876543210)";
    if (!form.city)   e.city  = "City is required.";
    if (!form.state)  e.state = "State is required.";
    if (!form.password || form.password.length < 8)
      e.password = "At least 8 characters.";
    if (form.password !== form.confirm_password)
      e.confirm_password = "Passwords don't match.";
    return e;
  };

  const handleSubmit = async () => {
    const e = validate();
    if (Object.keys(e).length) return setErrors(e);
    setErrors({});
    setAlert("");
    setLoading(true);

    try {
      // 1. Complete profile — use tokens.access directly (not from localStorage yet)
      const profileRes = await fetch("http://127.0.0.1:8000/api/auth/complete-profile/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${tokens.access}`,
        },
        body: JSON.stringify({
          full_name:    form.full_name,
          phone_number: form.phone_number,
          city:         form.city,
          state:        form.state,
          role:         form.role,
        }),
      });
      const profileData = await profileRes.json();
      if (!profileRes.ok) throw new Error(profileData?.error || "Profile update failed.");

      // 2. Set password
      const passRes = await fetch("http://127.0.0.1:8000/api/auth/set-password/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${tokens.access}`,
        },
        body: JSON.stringify({
          password:         form.password,
          confirm_password: form.confirm_password,
        }),
      });
      const passData = await passRes.json();
      if (!passRes.ok) throw new Error(passData?.error || "Password set failed.");

      saveLogin(profileData.user, tokens);
      onSuccess();
    } catch (err) {
      setAlert(err.message || "Something went wrong.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <AuthLayout step={3} total={3}>
      <div className="space-y-6">
        <div>
          <p className="text-xs font-semibold text-amber-500 tracking-widest uppercase mb-2">
            Almost there
          </p>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Complete your profile</h1>
          <p className="text-slate-500 text-sm mt-2">
            Just a few details to personalise your experience.
          </p>
        </div>

        <Card className="p-6 space-y-4">
          {alert && <Alert type="error" message={alert} />}

          {/* Role selector */}
          <div>
            <p className="text-sm font-medium text-slate-700 mb-2">I am a…</p>
            <div className="grid grid-cols-2 gap-2">
              {ROLES.map((r) => (
                <button
                  key={r.value}
                  onClick={() => upd("role", r.value)}
                  className={`p-3 rounded-xl border text-left transition-all duration-150
                    ${form.role === r.value
                      ? "border-amber-400 bg-amber-50"
                      : "border-slate-200 hover:border-slate-300 bg-white"}`}
                >
                  <div className="text-lg mb-1">{r.icon}</div>
                  <p className="text-xs font-medium text-slate-700">{r.label}</p>
                </button>
              ))}
            </div>
          </div>

          <Input
            label="Full name" placeholder="John Doe"
            value={form.full_name} error={errors.full_name}
            onChange={(e) => upd("full_name", e.target.value)}
          />
          <Input
            label="Phone number" placeholder="+919876543210"
            value={form.phone_number} error={errors.phone_number}
            onChange={(e) => upd("phone_number", e.target.value)}
          />

          <div className="grid grid-cols-2 gap-3">
            <Input label="City" placeholder="Kochi" value={form.city}
              error={errors.city} onChange={(e) => upd("city", e.target.value)} />
            <Input label="State" placeholder="Kerala" value={form.state}
              error={errors.state} onChange={(e) => upd("state", e.target.value)} />
          </div>

          <div className="border-t border-slate-100 pt-4 space-y-3">
            <p className="text-sm font-medium text-slate-700">Set a password</p>
            <Input
              label="Password" type="password" placeholder="Min. 8 characters"
              value={form.password} error={errors.password}
              onChange={(e) => upd("password", e.target.value)}
            />
            <Input
              label="Confirm password" type="password" placeholder="Repeat password"
              value={form.confirm_password} error={errors.confirm_password}
              onChange={(e) => upd("confirm_password", e.target.value)}
            />
          </div>

          <Button loading={loading} onClick={handleSubmit} className="w-full">
            Complete setup →
          </Button>
        </Card>
      </div>
    </AuthLayout>
  );
}
