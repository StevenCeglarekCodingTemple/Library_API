from app.blueprints.items import items_bp
from app.utils.util import token_required
from .schemas import item_schema, items_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Items, db
from app.extensions import limiter

# Create Item
@items_bp.route('', methods=['POST'])
def create_item():
    try:
        data = item_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    new_item = Items(**data)
    db.session.add(new_item)
    db.session.commit()
    return item_schema.jsonify(new_item), 201