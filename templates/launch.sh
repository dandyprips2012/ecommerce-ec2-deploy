#!/bin/bash
# Start all backend services, frontend, and automation

# Kill any existing processes on the ports
pkill -f "python.*app.py" || true
pkill -f "node.*automate.js" || true
pkill -f "react-scripts" || true

cd backend/product-service
source venv/bin/activate
python app/app.py > /tmp/product.log 2>&1 &
cd ../..

cd backend/order-service
source venv/bin/activate
python app/app.py > /tmp/order.log 2>&1 &
cd ../..

cd backend/inventory-service
source venv/bin/activate
python app/app.py > /tmp/inventory.log 2>&1 &
cd ../..

sleep 10

# Seed the databases (already done by deploy.py, but keep for idempotency)
cd backend
source product-service/venv/bin/activate
python seed.py
cd ..

# Start frontend
cd frontend/frontend
PORT=3006 npm start > /tmp/frontend.log 2>&1 &
cd ../..

sleep 20

# Start automation (the script name is always automate.js after copying)
cd automation
node automate.js > /tmp/automation.log 2>&1 &

echo "All services started."
echo "Frontend: http://localhost:3006"
echo "Backend APIs on ports 5001,5002,5003"