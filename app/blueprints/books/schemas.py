from app.extensions import ma
from app.models import Books

class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Books #Creates a schema that validates the data as defined by our Loans Model

book_schema = BookSchema() 
books_schema = BookSchema(many=True) #Allows this schema to translate a list of User objects all at once