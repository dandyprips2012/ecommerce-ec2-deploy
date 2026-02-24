import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, List, ListItem, ListItemText, Button, CircularProgress } from '@mui/material';

function OrderList() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchOrders = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:5002/api/orders');
      const data = await res.json();
      setOrders(data);
      console.log('Orders fetched:', data);
    } catch (err) {
      console.error('Error fetching orders:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchOrders(); }, []);

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>Orders</Typography>
        <Button variant="contained" onClick={fetchOrders} sx={{ mb: 2 }}>Refresh</Button>
        {loading ? <CircularProgress /> : (
          <List>
            {orders.map(o => (
              <ListItem key={o.id}>
                <ListItemText
                  primary={`Order #${o.id} - Product ${o.product_id}`}
                  secondary={`Quantity: ${o.quantity} | Total: $${o.total_price} | ${new Date(o.created_at).toLocaleString()}`}
                />
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
}

export default OrderList;