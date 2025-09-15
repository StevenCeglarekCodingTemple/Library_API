from app.blueprints.books import books_bp
from .schemas import book_schema, books_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.models import Books, db

#CREATE BOOK ROUTE
@books_bp.route('', methods=['POST']) #route servers as the trigger for the function below.
def create_book():
    try:
        data = book_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    

    new_book = Books(**data) #Creating Book object
    db.session.add(new_book)
    db.session.commit()
    return book_schema.jsonify(new_book), 201

#Read Books
@books_bp.route('', methods=['GET']) #Endpoint to get book information
def read_books():
    books = db.session.query(Books).all()
    return books_schema.jsonify(books), 200

#Read Individual Book - Using a Dynamic Endpoint
@books_bp.route('<int:book_id>', methods=['GET'])
def read_book(book_id):
    book = db.session.get(Books, book_id)
    return book_schema.jsonify(book), 200

#Delete a book
@books_bp.route('<int:book_id>', methods=['DELETE'])
def delete_book(book_id):
    book = db.session.get(Books, book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted book {book_id}"}), 200

#Update a Books
@books_bp.route('<int:book_id>', methods=['PUT'])
def update_book(book_id):
    book = db.session.get(Books, book_id) #Query for our book to update

    if not book: #Checking if I got a book
        return jsonify({"message": "book not found"}), 404  #if not return error message
    
    try:
        book_data = book_schema.load(request.json) #Validating updates
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    for key, value in book_data.items(): #Looping over attributes and values from book data dictionary
        setattr(book, key, value) # setting Object, Attribute, Value to replace

    db.session.commit()
    return book_schema.jsonify(book), 200