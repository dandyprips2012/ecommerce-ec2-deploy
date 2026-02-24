import React, { useState } from 'react';
import { Card, CardContent, Typography, TextField, Button, Box, Alert } from '@mui/material';

function AddProduct() {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [price, setPrice] = useState('');
  const [message, setMessage] = useState(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:5001/api/products', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description, price: parseFloat(price) })
      });
      if (res.ok) {
        setMessage('Product added successfully');
        setSuccess(true);
        setName('');
        setDescription('');
        setPrice('');
      } else {
        setMessage('Error adding product');
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
        <Typography variant="h5" gutterBottom>Add Product</Typography>
        <Box component="form" onSubmit={handleSubmit}>
          <TextField fullWidth label="Name" value={name} onChange={(e) => setName(e.target.value)} required margin="normal" />
          <TextField fullWidth label="Description" value={description} onChange={(e) => setDescription(e.target.value)} margin="normal" />
          <TextField fullWidth label="Price" type="number" value={price} onChange={(e) => setPrice(e.target.value)} required margin="normal" inputProps={{ min: 0, step: 0.01 }} />
          <Button type="submit" variant="contained" color="primary" sx={{ mt: 2 }}>Add Product</Button>
          {message && <Alert severity={success ? "success" : "error"} sx={{ mt: 2 }}>{message}</Alert>}
        </Box>
      </CardContent>
    </Card>
  );
}

export default AddProduct;