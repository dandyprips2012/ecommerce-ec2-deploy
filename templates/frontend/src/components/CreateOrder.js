import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, TextField, Button, MenuItem, Box, Alert } from '@mui/material';

function CreateOrder() {
  const [products, setProducts] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [quantity, setQuantity] = useState(1);
  const [message, setMessage] = useState(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetch('http://localhost:5001/api/products')
      .then(res => res.json())
      .then(data => setProducts(data))
      .catch(console.error);
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const product = products.find(p => p.id === parseInt(selectedProduct));
    if (!product) return;
    const total_price = product.price * quantity;
    try {
      const res = await fetch('http://localhost:5002/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          product_id: product.id,
          quantity,
          total_price
        })
      });
      if (res.ok) {
        setMessage('Order created successfully');
        setSuccess(true);
        setSelectedProduct('');
        setQuantity(1);
      } else {
        const err = await res.json();
        setMessage(err.error || 'Error creating order');
        setSuccess(false);
      }
    } catch (err) {
      setMessage('Network error');
      setSuccess(false);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>Create Order</Typography>
        <Box component="form" onSubmit={handleSubmit}>
          <TextField
            select
            fullWidth
            label="Product"
            value={selectedProduct}
            onChange={(e) => setSelectedProduct(e.target.value)}
            required
            margin="normal"
          >
            {products.map(p => (
              <MenuItem key={p.id} value={p.id}>{p.name} - ${p.price}</MenuItem>
            ))}
          </TextField>
          <TextField
            fullWidth
            label="Quantity"
            type="number"
            value={quantity}
            onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
            required
            margin="normal"
            inputProps={{ min: 1 }}
          />
          <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }}>Place Order</Button>
          {message && <Alert severity={success ? "success" : "error"} sx={{ mt: 2 }}>{message}</Alert>}
        </Box>
      </CardContent>
    </Card>
  );
}

export default CreateOrder;