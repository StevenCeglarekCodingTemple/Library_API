from app.extensions import ma
from app.models import Items, ItemOrders


class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Items
        
item_schema = ItemSchema()
items_schema = ItemSchema(many=True)


class ItemOrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ItemOrders
        include_fk = True
        
item_order_schema = ItemOrderSchema()
item_orders_schema = ItemOrderSchema(many=True)