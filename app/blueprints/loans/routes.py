from app.blueprints.loans import loans_bp
from .schemas import loan_schema, loans_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Loans, db, Books
from app.blueprints.books.schemas import books_schema
from app.blueprints.users.schemas import user_schema
from app.extensions import limiter, cache

#CREATE LOAN ROUTE
@loans_bp.route('', methods=['POST']) #route servers as the trigger for the function below.
def create_loan():
    try:
        data = loan_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    
    new_loan = Loans(**data)
    
    db.session.add(new_loan)
    db.session.commit()
    return loan_schema.jsonify(new_loan), 201

#Add book to loan
@loans_bp.route('/<int:loan_id>/add-book/<int:book_id>', methods=['PUT'])
@limiter.limit("600 per day", override_defaults=True)
def add_book(loan_id, book_id):
    loan = db.session.get(Loans, loan_id)
    book = db.session.get(Books, book_id)

    if book not in loan.books: #checking to see if a relationship already exist between loan and book
        loan.books.append(book) #creating a relationship between loan and book
        db.session.commit()
        return jsonify({
            'message': f'successfully add {book.title} to loan',
            'loan': loan_schema.dump(loan),  #use dump when the schema is adding just a piece of the return message
            'books': books_schema.dump(loan.books) #using the books_schema to serialize the list of books related to the loan
        }), 200
    
    return jsonify("This book is already on the loan"), 400

#Remove book from loan
@loans_bp.route('/<int:loan_id>/remove-book/<int:book_id>', methods=['PUT'])
@limiter.limit("200 per day", override_defaults=True)
def remove_book(loan_id, book_id):
    loan = db.session.get(Loans, loan_id)
    book = db.session.get(Books, book_id)

    if book in loan.books: #checking to see if a relationship already exist between loan and book
        loan.books.remove(book) #removing the relationship between loan and book
        db.session.commit()
        return jsonify({
            'message': f'successfully removed {book.title} from loan',
            'loan': loan_schema.dump(loan),  #use dump when the schema is adding just a piece of the return message
            'books': books_schema.dump(loan.books) #using the books_schema to serialize the list of books related to the loan
        }), 200
    
    return jsonify("This book is no on the loan"), 400

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