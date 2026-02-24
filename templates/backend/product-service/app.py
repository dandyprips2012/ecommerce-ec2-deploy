import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import requests

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins="http://localhost:3006")

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///products.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    price = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description, "price": self.price}

with app.app_context():
    db.create_all()
    logger.info("Product database tables created")

@app.route('/api/products', methods=['GET'])
def get_products():
    logger.info("GET /api/products")
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products])

@app.route('/api/products', methods=['POST'])
def create_product():
    data = request.get_json()
    logger.info(f"POST /api/products data: {data}")
    if not data or not all(k in data for k in ('name','price')):
        logger.error("Invalid product data")
        return jsonify({"error": "Invalid input"}), 400
    product = Product(name=data['name'], description=data.get('description',''), price=data['price'])
    db.session.add(product)
    db.session.commit()
    logger.info(f"Product created with ID: {product.id}")

    try:
        inv_payload = {"product_id": product.id, "quantity": 0}
        requests.post("http://localhost:5003/api/inventory", json=inv_payload, timeout=2)
        logger.debug("Inventory service notified")
    except Exception as e:
        logger.error(f"Failed to notify inventory: {e}")

    return jsonify(product.to_dict()), 201

@app.route('/api/products/<int:id>', methods=['PUT'])
def update_product(id):
    data = request.get_json()
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Not found"}), 404
    if 'name' in data: product.name = data['name']
    if 'description' in data: product.description = data['description']
    if 'price' in data: product.price = data['price']
    db.session.commit()
    logger.info(f"Product {id} updated")
    return jsonify(product.to_dict())

@app.route('/api/products/<int:id>', methods=['DELETE'])
def delete_product(id):
    product = Product.query.get(id)
    if not product:
        return jsonify({"error": "Not found"}), 404
    db.session.delete(product)
    db.session.commit()
    logger.info(f"Product {id} deleted")
    return '', 204

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)