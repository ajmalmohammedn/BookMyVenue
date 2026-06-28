import { useState } from "react";
import { AuthProvider } from "./context/AuthContext";
import AuthPage  from "./pages/AuthPage";
import HomePage  from "./pages/HomePage";

export default function App() {
  return (
    <AuthProvider>
      <AppRouter />
    </AuthProvider>
  );
}

function AppRouter() {
  const [page, setPage] = useState("home");

  if (page === "auth") {
    return <AuthPage onDone={() => setPage("home")} />;
  }

  return <HomePage onGetStarted={() => setPage("auth")} />;
}
