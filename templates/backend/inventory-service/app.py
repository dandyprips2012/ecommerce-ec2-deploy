import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="http://localhost:3006")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, unique=True, nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)

    def to_dict(self):
        return {"id": self.id, "product_id": self.product_id, "quantity": self.quantity}

with app.app_context():
    db.create_all()
    logger.info("Inventory database tables created")

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    logger.info("GET /api/inventory")
    items = Inventory.query.all()
    return jsonify([i.to_dict() for i in items])

@app.route('/api/inventory', methods=['POST'])
def create_inventory():
    data = request.get_json()
    logger.info(f"POST /api/inventory data: {data}")
    if not data or 'product_id' not in data:
        return jsonify({"error": "Invalid input"}), 400
    existing = Inventory.query.filter_by(product_id=data['product_id']).first()
    if existing:
        return jsonify(existing.to_dict()), 200
    inv = Inventory(product_id=data['product_id'], quantity=data.get('quantity', 0))
    db.session.add(inv)
    db.session.commit()
    logger.info(f"Inventory created for product {data['product_id']}")
    return jsonify(inv.to_dict()), 201

@app.route('/api/inventory/<int:product_id>', methods=['PUT'])
def update_inventory(product_id):
    data = request.get_json()
    inv = Inventory.query.filter_by(product_id=product_id).first()
    if not inv:
        return jsonify({"error": "Not found"}), 404
    if 'quantity' in data:
        inv.quantity = data['quantity']
        db.session.commit()
        logger.info(f"Inventory for product {product_id} updated to {inv.quantity}")
    return jsonify(inv.to_dict())

@app.route('/api/inventory/reserve', methods=['POST'])
def reserve():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    inv = Inventory.query.filter_by(product_id=product_id).first()
    if not inv or inv.quantity < quantity:
        logger.warning(f"Insufficient stock for product {product_id}")
        return jsonify({"error": "Insufficient stock"}), 400
    inv.quantity -= quantity
    db.session.commit()
    logger.info(f"Reserved {quantity} of product {product_id}, remaining {inv.quantity}")
    return jsonify(inv.to_dict())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)