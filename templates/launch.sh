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

# Seed the databases with retry (up to 5 times) – gives tables time to be created
cd backend
max_retries=5
retry_count=0
until [ $retry_count -ge $max_retries ]
do
    source product-service/venv/bin/activate
    python seed.py
    if [ $? -eq 0 ]; then
        echo "Seeding successful"
        break
    else
        retry_count=$((retry_count+1))
        echo "Seeding failed, retrying in 5 seconds... (Attempt $retry_count/$max_retries)"
        sleep 5
    fi
done
cd ..

# Start frontend (correct path: frontend/, not frontend/frontend)
cd frontend
PORT=3006 npm start > /tmp/frontend.log 2>&1 &
cd ..

sleep 20

# Start automation
cd automation
node automate.js > /tmp/automation.log 2>&1 &

echo "All services started."
echo "Frontend: http://localhost:3006"
echo "Backend APIs on ports 5001,5002,5003"