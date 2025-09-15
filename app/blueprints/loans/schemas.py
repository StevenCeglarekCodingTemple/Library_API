from app.extensions import ma
from app.models import Loans

class LoanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Loans #Creates a schema that validates the data as defined by our Loans Model
        include_fk = True

loan_schema = LoanSchema() 
loans_schema = LoanSchema(many=True) #Allows this schema to translate a list of User objects all at once