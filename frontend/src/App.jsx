import { useState } from 'react'
import { AuthProvider } from './context/AuthContext'
import CheckEmailStep      from './components/auth/CheckEmailStep'
import VerifyOTPStep       from './components/auth/VerifyOTPStep'
// import LoginStep           from './components/auth/LoginStep'
// import CompleteProfileStep from './components/auth/CompleteProfileStep'

function AuthFlow({ onDone }) {
  const [step, setStep]   = useState("email")
  const [state, setState] = useState({
    email:   "",
    tokens:  null,
    otpType: "signup",
  })

  const update = (patch) => setState((s) => ({ ...s, ...patch }))

  if (step === "email") return (
    <CheckEmailStep
      onNext={({ email, flow }) => {
        update({ email })
        if (flow === "login") {
          setStep("login")
        } else {
          update({ otpType: "signup" })
          setStep("otp")
        }
      }}
    />
  )

  if (step === "otp") return (
    <VerifyOTPStep
      email={state.email}
      otpType={state.otpType}
      onBack={() => setStep("email")}
      onNext={({ tokens }) => {
        update({ tokens })
        setStep("profile")
      }}
    />
  )

  if (step === "login") return (
    <LoginStep
      email={state.email}
      onSuccess={onDone}
      onBack={(action) => {
        if (action === "forgot") {
          update({ otpType: "password_reset" })
          setStep("otp")
        } else {
          setStep("email")
        }
      }}
    />
  )

  if (step === "profile") return (
    <CompleteProfileStep
      tokens={state.tokens}
      onSuccess={onDone}
    />
  )

  return null
}

function App() {
  return (
    <AuthProvider>
      <AuthFlow onDone={() => console.log("Auth complete!")} />
    </AuthProvider>
  )
}

export default App