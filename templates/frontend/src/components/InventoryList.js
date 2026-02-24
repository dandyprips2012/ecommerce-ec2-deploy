import React, { useState, useEffect } from 'react';
import { Card, CardContent, Typography, List, ListItem, ListItemText, Button, CircularProgress, TextField, Box } from '@mui/material';

function InventoryList() {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [editQuantities, setEditQuantities] = useState({});

  const fetchInventory = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:5003/api/inventory');
      const data = await res.json();
      setInventory(data);
      const edits = {};
      data.forEach(i => { edits[i.product_id] = i.quantity; });
      setEditQuantities(edits);
      console.log('Inventory fetched:', data);
    } catch (err) {
      console.error('Error fetching inventory:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchInventory(); }, []);

  const handleUpdate = async (productId) => {
    const newQty = editQuantities[productId];
    try {
      const res = await fetch(`http://localhost:5003/api/inventory/${productId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ quantity: newQty })
      });
      if (res.ok) {
        fetchInventory();
      }
    } catch (err) {
      console.error('Update error:', err);
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h5" gutterBottom>Inventory</Typography>
        <Button variant="contained" onClick={fetchInventory} sx={{ mb: 2 }}>Refresh</Button>
        {loading ? <CircularProgress /> : (
          <List>
            {inventory.map(i => (
              <ListItem key={i.product_id}>
                <ListItemText primary={`Product ID: ${i.product_id}`} secondary={`Current stock: ${i.quantity}`} />
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <TextField
                    size="small"
                    type="number"
                    value={editQuantities[i.product_id] || 0}
                    onChange={(e) => setEditQuantities({...editQuantities, [i.product_id]: parseInt(e.target.value) || 0})}
                    inputProps={{ min: 0, style: { width: '80px' } }}
                  />
                  <Button variant="outlined" size="small" onClick={() => handleUpdate(i.product_id)}>Update</Button>
                </Box>
              </ListItem>
            ))}
          </List>
        )}
      </CardContent>
    </Card>
  );
}

export default InventoryList;