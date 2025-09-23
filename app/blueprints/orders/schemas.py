from app.extensions import ma
from app.models import Orders

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Orders #Creates a schema that validates the data as defined by our Loans Model
        include_fk = True

order_schema = OrderSchema() 
orders_schema = OrderSchema(many=True) #Allows this schema to translate a list of User objects all at once