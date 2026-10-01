import { useState } from "react";
import { navigate } from "../components/RouteView";
import { useAuth } from "../context/AuthContext";
import { authApi } from "../services/authApi";

export default function Register() {
  const { register } = useAuth();
  const [form,setForm]=useState({name:"",email:"",password:""}); const [loading,setLoading]=useState(false); const [error,setError]=useState("");
  const next=new URLSearchParams(window.location.search).get("next")||"/";
  async function submit(e){e.preventDefault();setLoading(true);setError("");try{await register(form);navigate(next)}catch(x){setError(x.message)}finally{setLoading(false)}}
  return <div className="page-shell"><section className="auth-card">
    <span className="eyebrow">Create your account</span><h1>Join enj0y Solution</h1><p className="muted">One account for your cart and orders.</p>
    {error&&<p className="form-error" role="alert">{error}</p>}
    <form className="form-stack" onSubmit={submit}>
      <label>Full name<input value={form.name} onChange={e=>setForm({...form,name:e.target.value})} required maxLength={255}/></label>
      <label>Email<input type="email" value={form.email} onChange={e=>setForm({...form,email:e.target.value})} required/></label>
      <label>Password<input type="password" value={form.password} onChange={e=>setForm({...form,password:e.target.value})} required minLength={8}/></label>
      <button className="button button--primary" disabled={loading}>{loading?"Creating account...":"Create account"}</button>
    </form>
    <div className="auth-divider"><span>or</span></div><a className="button button--oauth" href={authApi.googleLoginUrl()}>Continue with Google</a>
    <p className="auth-switch">Already have an account? <button onClick={()=>navigate(`/login?next=${encodeURIComponent(next)}`)}>Sign in</button></p>
  </section></div>;
}