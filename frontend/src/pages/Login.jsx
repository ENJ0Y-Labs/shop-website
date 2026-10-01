import { useState } from "react";
import { navigate } from "../components/RouteView";
import { useAuth } from "../context/AuthContext";
import { authApi } from "../services/authApi";

export default function Login() {
  const { login } = useAuth();
  const [form, setForm] = useState({ email: "", password: "" });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const next = new URLSearchParams(window.location.search).get("next") || "/";
  async function submit(event) {
    event.preventDefault(); setLoading(true); setError("");
    try { await login(form); navigate(next); } catch (e) { setError(e.message); } finally { setLoading(false); }
  }
  return <div className="page-shell"><section className="auth-card">
    <span className="eyebrow">Welcome back</span><h1>Sign in</h1><p className="muted">Access your cart, checkout, and order history.</p>
    {error && <p className="form-error" role="alert">{error}</p>}
    <form className="form-stack" onSubmit={submit}>
      <label>Email<input type="email" value={form.email} onChange={(e)=>setForm({...form,email:e.target.value})} required /></label>
      <label>Password<input type="password" value={form.password} onChange={(e)=>setForm({...form,password:e.target.value})} required /></label>
      <button className="button button--primary" disabled={loading}>{loading ? "Signing in..." : "Sign in"}</button>
    </form>
    <div className="auth-divider"><span>or</span></div>
    <a className="button button--oauth" href={authApi.googleLoginUrl()}>Continue with Google</a>
    <p className="auth-switch">New here? <button onClick={()=>navigate(`/register?next=${encodeURIComponent(next)}`)}>Create an account</button></p>
  </section></div>;
}