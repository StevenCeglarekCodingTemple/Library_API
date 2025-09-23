from app.blueprints.orders import orders_bp
from app.utils.util import token_required
from .schemas import order_schema, orders_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Orders, db, Items, ItemOrders
from app.extensions import limiter

# Create Order
@orders_bp.route('', methods=['POST'])
@token_required
def create_order(user_id):
    try:
        data = order_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_order = Orders(**data)
    db.session.add(new_order)
    db.session.commit()
    return order_schema.jsonify(new_order), 201


# Add item to Order
@orders_bp.route('/<int:order_id>/add-item/<int:item_id>/<int:qty>', methods=['PUT'])
def add_item_to_order(order_id, item_id, qty):
    
    new_item_order = ItemOrders(item_id=item_id, order_id=order_id, quantity=qty)
    db.session.add(new_item_order)
    db.session.commit()
    return jsonify({'message': f"Successfully added item to Order"})
    