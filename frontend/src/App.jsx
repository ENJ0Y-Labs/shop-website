import Checkout from "./pages/Checkout";

function App() {
  if (window.location.pathname === "/checkout") {
    return <Checkout />;
  }

  return (
    <main className="app">
      <h1>enj0y Solution</h1>
      <p>Shop foundation initialized.</p>
      <a href="/checkout">Checkout</a>
    </main>
  );
}

export default App;
