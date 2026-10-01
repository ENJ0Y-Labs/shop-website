import { useEffect,useState } from "react";
import { EmptyState,PageState,navigate } from "../components/RouteView";
import { orderApi } from "../services/orderApi";
const money=k=>new Intl.NumberFormat("en-NG",{style:"currency",currency:"NGN"}).format((k??0)/100);
export default function Orders(){
 const [orders,setOrders]=useState([]),[loading,setLoading]=useState(true),[error,setError]=useState("");
 useEffect(()=>{orderApi.list().then(r=>setOrders(r.orders)).catch(e=>setError(e.message)).finally(()=>setLoading(false))},[]);
 if(loading)return <PageState message="Loading your orders..."/>; if(error)return <PageState message={error} error/>;
 if(!orders.length)return <div className="page-shell"><section className="container content-narrow"><EmptyState title="No orders yet." message="Your future receipts will live here." action={()=>navigate("/")} actionLabel="Start shopping"/></section></div>;
 return <div className="page-shell"><section className="container content-narrow"><div className="section-heading"><div><span className="eyebrow">Account</span><h1>Order history</h1></div></div>
 <div className="order-list">{orders.map(o=><button className="order-card" key={o.id} onClick={()=>navigate(`/order/${o.id}`)}><div><strong>{o.order_number}</strong><span>{new Date(o.created_at).toLocaleDateString()}</span></div><div><span className="status-pill">{o.status}</span><strong>{money(o.total_amount)}</strong></div></button>)}</div>
 </section></div>;
}