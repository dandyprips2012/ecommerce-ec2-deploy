import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, List, ListItem, ListItemText, Button, CircularProgress, Box } from '@mui/material';

function ProductList() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchProducts = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:5001/api/products');
      const data = await res.json();
      setProducts(data);
      console.log('Products fetched:', data);
    } catch (err) {
      console.error('Error fetching products:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchProducts(); }, []);

  const handleDelete = async (id) => {
    try {
      await fetch(`http://localhost:5001/api/products/${id}`, { method: 'DELETE' });
      fetchProducts();
    } catch (err) {
      console.error('Delete error:', err);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>Products</Typography>
        <Button variant="contained" onClick={fetchProducts} sx={{ mb: 2 }}>Refresh</Button>
        {loading ? <CircularProgress /> : (
          <List>
            {products.map(p => (
              <ListItem key={p.id} secondaryAction={
                <Button color="error" onClick={() => handleDelete(p.id)}>Delete</Button>
              } data-product-id={p.id}>
                <ListItemText primary={p.name} secondary={`$${p.price} - ${p.description || ''}`} />
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
}

export default ProductList;