import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import ProductList from './components/ProductList';
import AddProduct from './components/AddProduct';
import OrderList from './components/OrderList';
import CreateOrder from './components/CreateOrder';
import InventoryList from './components/InventoryList';

function App() {
  return (
    <Router>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            E‑commerce Platform
          </Typography>
          <Button color="inherit" component={Link} to="/">Products</Button>
          <Button color="inherit" component={Link} to="/add-product">Add Product</Button>
          <Button color="inherit" component={Link} to="/orders">Orders</Button>
          <Button color="inherit" component={Link} to="/create-order">Create Order</Button>
          <Button color="inherit" component={Link} to="/inventory">Inventory</Button>
        </Toolbar>
      </AppBar>
      <Container sx={{ mt: 4 }}>
        <Routes>
          <Route path="/" element={<ProductList />} />
          <Route path="/add-product" element={<AddProduct />} />
          <Route path="/orders" element={<OrderList />} />
          <Route path="/create-order" element={<CreateOrder />} />
          <Route path="/inventory" element={<InventoryList />} />
        </Routes>
      </Container>
    </Router>
  );
}

export default App;