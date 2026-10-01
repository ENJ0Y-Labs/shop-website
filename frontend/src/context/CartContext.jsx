import { createContext,useContext,useEffect,useMemo,useState } from "react";
import { useAuth } from "./AuthContext";
import { cartApi } from "../services/cartApi";
import { addToLocalCart,clearLocalCart,getLocalCart,hasLocalCartItems,removeFromLocalCart,updateLocalCartItem } from "../services/cartStorage";
const CartContext=createContext(null);
function localCartView(items){return{items,item_count:items.reduce((sum,item)=>sum+item.quantity,0),total:null};}
export function CartProvider({children}){
 const {user}=useAuth(); const [cart,setCart]=useState(null); const [loading,setLoading]=useState(true);
 useEffect(()=>{
  let cancelled=false;
  async function load(){
   setLoading(true);
   if(!user){if(!cancelled)setCart(localCartView(getLocalCart()));setLoading(false);return;}
   try{
    const local=getLocalCart(); const response=local.length?await cartApi.merge(local):await cartApi.get();
    if(local.length)clearLocalCart();
    if(!cancelled)setCart(response.cart);
   }catch{if(!cancelled)setCart(null)}finally{if(!cancelled)setLoading(false)}
  }
  load(); return()=>{cancelled=true};
 },[user]);
 useEffect(()=>{
  const refresh=async()=>{if(!user)return;try{const r=await cartApi.get();setCart(r.cart)}catch{}};
  window.addEventListener("cart-refresh",refresh); return()=>window.removeEventListener("cart-refresh",refresh);
 },[user]);
 function addVisitorItem(id,q=1){const items=addToLocalCart(id,q);setCart(localCartView(items));return items}
 function updateVisitorItem(id,q){const items=updateLocalCartItem(id,q);setCart(localCartView(items));return items}
 function removeVisitorItem(id){const items=removeFromLocalCart(id);setCart(localCartView(items));return items}
 function clearVisitorCart(){clearLocalCart();setCart(localCartView([]))}
 const value=useMemo(()=>({cart,loading,authenticated:Boolean(user),hasLocalItems:hasLocalCartItems(),addVisitorItem,updateVisitorItem,removeVisitorItem,clearVisitorCart}),[cart,loading,user]);
 return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}
export function useCart(){const context=useContext(CartContext);if(!context)throw new Error("useCart must be used within CartProvider");return context;}