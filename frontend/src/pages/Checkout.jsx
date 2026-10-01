import { useEffect,useMemo,useState } from "react";
import { PageState,navigate } from "../components/RouteView";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { orderApi } from "../services/orderApi";
const initialForm={name:"",email:"",phone:"",address:"",city:"",state:"",country:"Nigeria"};
const money=k=>new Intl.NumberFormat("en-NG",{style:"currency",currency:"NGN"}).format((k??0)/100);
export default function Checkout(){
 const {user,loading:authLoading,isAuthenticated}=useAuth(); const {cart}=useCart(); const [form,setForm]=useState(initialForm); const [submitting,setSubmitting]=useState(false); const [error,setError]=useState("");
 useEffect(()=>{if(user)setForm(c=>({...c,name:user.name??"",email:user.email??""}))},[user]); const total=useMemo(()=>cart?.total??0,[cart]);
 if(authLoading)return <PageState message="Checking your account..."/>; if(!isAuthenticated){navigate("/login?next=/checkout");return <PageState message="Redirecting to sign in..."/>}
 if(!cart?.items?.length)return <div className="page-shell"><section className="container content-narrow"><EmptyState title="Your cart is empty." message="Add something before checking out." action={()=>navigate("/")} actionLabel="Shop products"/></section></div>;
 function change(e){setForm(c=>({...c,[e.target.name]:e.target.value}))}
 async function submit(e){e.preventDefault();setSubmitting(true);setError("");try{const r=await orderApi.create(form);navigate(`/order/${r.order.id}`)}catch(x){setError(x.message)}finally{setSubmitting(false)}}
 return <div className="page-shell"><section className="container checkout-layout"><div><span className="eyebrow">Checkout</span><h1>Complete your order</h1><p className="muted">Your final price, stock, and total are verified by the server.</p>{error&&<p className="form-error" role="alert">{error}</p>}
 <form className="form-stack checkout-form" onSubmit={submit}><label>Full name<input name="name" value={form.name} onChange={change} required maxLength={255}/></label><label>Email<input name="email" type="email" value={form.email} onChange={change} required maxLength={255}/></label><label>Phone<input name="phone" value={form.phone} onChange={change} required maxLength={50}/></label><label>Address<input name="address" value={form.address} onChange={change} required maxLength={500}/></label><div className="checkout-grid"><label>City<input name="city" value={form.city} onChange={change} required maxLength={100}/></label><label>State<input name="state" value={form.state} onChange={change} required maxLength={100}/></label></div><label>Country<input name="country" value={form.country} onChange={change} required maxLength={100}/></label><button className="button button--primary" disabled={submitting}>{submitting?"Placing order...":"Place order · "+money(total)}</button></form></div>
 <aside className="checkout-summary-card"><span className="eyebrow">Summary</span><h2>{cart.item_count} item{cart.item_count===1?"":"s"}</h2>{cart.items.map(i=><div className="summary-line" key={i.id}><span>{i.product.name} × {i.quantity}</span><strong>{money(i.subtotal)}</strong></div>)}<div className="summary-total"><span>Total</span><strong>{money(total)}</strong></div></aside>
 </section></div>;
}