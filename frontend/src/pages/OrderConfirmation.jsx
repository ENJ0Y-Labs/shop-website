import { useEffect,useState } from "react";
import { PageState,navigate } from "../components/RouteView";
import { orderApi } from "../services/orderApi";
const money=k=>new Intl.NumberFormat("en-NG",{style:"currency",currency:"NGN"}).format((k??0)/100);
export default function OrderConfirmation({id}){
 const [order,setOrder]=useState(null),[loading,setLoading]=useState(true),[error,setError]=useState("");
 useEffect(()=>{orderApi.get(id).then(r=>setOrder(r.order)).catch(e=>setError(e.message)).finally(()=>setLoading(false))},[id]);
 if(loading)return <PageState message="Loading your order..."/>; if(error)return <PageState message={error} error/>;
 return <div className="page-shell"><section className="container content-narrow"><div className="success-card">
  <span className="success-mark">✓</span><span className="eyebrow">Order confirmed</span><h1>Thanks, {order.customer.name}.</h1><p>Your order <strong>{order.order_number}</strong> is confirmed.</p>
  <p className="muted">{new Date(order.created_at).toLocaleString()} · {order.status}</p>
  <div className="order-items">{order.items.map(i=><div className="order-item" key={i.id}><span>{i.product_name} × {i.quantity}</span><strong>{money(i.subtotal)}</strong></div>)}</div>
  <div className="cart-summary"><span>Total</span><strong>{money(order.total_amount)}</strong></div>
  <div className="cart-actions"><button className="button button--ghost" onClick={()=>navigate("/")}>Continue shopping</button><button className="button button--primary" onClick={()=>navigate("/orders")}>View orders</button></div>
 </div></section></div>;
}