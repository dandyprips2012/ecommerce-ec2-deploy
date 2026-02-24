import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests
from datetime import datetime

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="http://localhost:3006")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///orders.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    total_price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "product_id": self.product_id,
            "quantity": self.quantity,
            "total_price": self.total_price,
            "created_at": self.created_at.isoformat()
        }

with app.app_context():
    db.create_all()
    logger.info("Order database tables created")

@app.route('/api/orders', methods=['GET'])
def get_orders():
    logger.info("GET /api/orders")
    orders = Order.query.all()
    return jsonify([o.to_dict() for o in orders])

@app.route('/api/orders', methods=['POST'])
def create_order():
    data = request.get_json()
    logger.info(f"POST /api/orders data: {data}")
    if not data or not all(k in data for k in ('product_id','quantity','total_price')):
        logger.error("Invalid order data")
        return jsonify({"error": "Invalid input"}), 400

    try:
        inv_resp = requests.post("http://localhost:5003/api/inventory/reserve", json={
            "product_id": data['product_id'],
            "quantity": data['quantity']
        }, timeout=3)
        if inv_resp.status_code != 200:
            logger.error("Inventory reservation failed")
            return jsonify({"error": "Insufficient stock"}), 400
    except Exception as e:
        logger.error(f"Inventory service error: {e}")
        return jsonify({"error": "Inventory service unavailable"}), 503

    order = Order(
        product_id=data['product_id'],
        quantity=data['quantity'],
        total_price=data['total_price']
    )
    db.session.add(order)
    db.session.commit()
    logger.info(f"Order created with ID: {order.id}")
    return jsonify(order.to_dict()), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug=True)