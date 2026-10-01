import { RouteView,ProtectedRoute,PageState } from "./components/RouteView";
import Layout from "./components/Layout";
import Shop from "./pages/Shop";
import ProductDetails from "./pages/ProductDetails";
import Cart from "./pages/Cart";
import Checkout from "./pages/Checkout";
import OrderConfirmation from "./pages/OrderConfirmation";
import Orders from "./pages/Orders";
import Login from "./pages/Login";
import Register from "./pages/Register";

function renderRoute(path){
 if(path==="/")return <Shop/>;
 if(path==="/cart")return <Cart/>;
 if(path==="/checkout")return <ProtectedRoute><Checkout/></ProtectedRoute>;
 if(path==="/orders")return <ProtectedRoute><Orders/></ProtectedRoute>;
 if(path.startsWith("/order/"))return <ProtectedRoute><OrderConfirmation id={path.split("/")[2]}/></ProtectedRoute>;
 if(path.startsWith("/products/"))return <ProductDetails id={path.split("/")[2]}/>;
 if(path==="/login")return <Login/>;
 if(path==="/register")return <Register/>;
 return <PageState message="Page not found." error/>;
}
export default function App(){return <RouteView>{path=><Layout>{renderRoute(path)}</Layout>}</RouteView>}