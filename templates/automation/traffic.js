const fetch = require('node-fetch');

const BASE_URL = 'http://localhost';

const productNames = ['Laptop', 'Mouse', 'Keyboard', 'Monitor', 'USB Cable', 'Webcam', 'Headset', 'SSD', 'RAM', 'GPU'];
const descriptions = ['High performance', 'Ergonomic', 'Mechanical', '4K Ultra HD', 'Fast charging', 'Noise cancelling', '1TB storage', '16GB', 'RTX 4080'];

async function randomDelay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function createProduct() {
  const name = productNames[Math.floor(Math.random() * productNames.length)];
  const description = descriptions[Math.floor(Math.random() * descriptions.length)];
  const price = (Math.random() * 500 + 20).toFixed(2);
  const payload = { name, description, price: parseFloat(price) };

  console.log(`Creating product: ${name}`);
  const response = await fetch(`${BASE_URL}:5001/api/products`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!response.ok) throw new Error(`Create product failed: ${response.status}`);
  const product = await response.json();
  console.log(`Product created with ID: ${product.id}`);
  return product;
}

async function getProductIdByName(name) {
  const response = await fetch(`${BASE_URL}:5001/api/products`);
  if (!response.ok) throw new Error(`Fetch products failed: ${response.status}`);
  const products = await response.json();
  const found = products.find(p => p.name === name);
  return found ? found.id : null;
}

async function updateInventory(productId, quantity) {
  console.log(`Updating inventory for product ${productId} to ${quantity}`);
  const response = await fetch(`${BASE_URL}:5003/api/inventory/${productId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ quantity })
  });
  if (!response.ok) throw new Error(`Update inventory failed: ${response.status}`);
  return response.json();
}

async function createOrder(productId, quantity, totalPrice) {
  console.log(`Placing order for product ${productId}, quantity ${quantity}`);
  const response = await fetch(`${BASE_URL}:5002/api/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      product_id: productId,
      quantity,
      total_price: totalPrice
    })
  });
  if (!response.ok) {
    const err = await response.json();
    throw new Error(`Create order failed: ${err.error || response.status}`);
  }
  const order = await response.json();
  console.log(`Order created: ${order.id}`);
  return order;
}

async function runCycle() {
  try {
    // 1. Create a new product
    const product = await createProduct();
    await randomDelay(1000);

    // 2. Update inventory for that product (ensure stock)
    await updateInventory(product.id, 100);
    await randomDelay(1000);

    // 3. Place an order for 2 units
    const total = product.price * 2;
    await createOrder(product.id, 2, total);
    await randomDelay(2000);

    // 4. Fetch orders and products (just to generate GET traffic)
    await fetch(`${BASE_URL}:5002/api/orders`);
    await fetch(`${BASE_URL}:5001/api/products`);
    console.log('Cycle completed successfully\n');
  } catch (error) {
    console.error('Cycle error:', error.message);
  }
}

async function main() {
  console.log('Traffic generator started. Will run a cycle every 25 seconds.');
  while (true) {
    await runCycle();
    await randomDelay(25000); // 25 seconds between cycles
  }
}

main().catch(console.error);