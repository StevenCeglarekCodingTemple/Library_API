from app.blueprints.loans import loans_bp
from .schemas import loan_schema, loans_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Loans, db

#CREATE LOAN ROUTE
@loans_bp.route('', methods=['POST']) #route servers as the trigger for the function below.
def create_loan():
    try:
        print(request.json)
        data = loan_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    

    new_loan = Loans(**data) #Creating Loan object
    db.session.add(new_loan)
    db.session.commit()
    return loan_schema.jsonify(new_loan), 201

#Read Loans
@loans_bp.route('', methods=['GET']) #Endpoint to get loan information
def read_loans():
    loans = db.session.query(Loans).all()
    return loans_schema.jsonify(loans), 200

#Read Individual Loan - Using a Dynamic Endpoint
@loans_bp.route('<int:loan_id>', methods=['GET'])
def read_loan(loan_id):
    loan = db.session.get(Loans, loan_id)
    return loan_schema.jsonify(loan), 200

#Delete a Loan
@loans_bp.route('<int:loan_id>', methods=['DELETE'])
def delete_loan(loan_id):
    loan = db.session.get(Loans, loan_id)
    db.session.delete(loan)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted loan {loan_id}"}), 200

#Update a Loan
@loans_bp.route('<int:loan_id>', methods=['PUT'])
def update_loan(loan_id):
    loan = db.session.get(Loans, loan_id) #Query for our loan to update

    if not loan: #Checking if I got a loan
        return jsonify({"message": "loan not found"}), 404  #if not return error message
    
    try:
        loan_data = loan_schema.load(request.json) #Validating updates
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    for key, value in loan_data.items(): #Looping over attributes and values from loan data dictionary
        setattr(loan, key, value) # setting Object, Attribute, Value to replace

    db.session.commit()
    return loan_schema.jsonify(loan), 200