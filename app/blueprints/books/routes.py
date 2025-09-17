from app.blueprints.books import books_bp
from .schemas import book_schema, books_schema
from flask import request, jsonify
from marshmallow import ValidationError
from app.extensions import limiter, cache
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
@cache.cached(timeout=30) 
def read_books():
    try:
        page = int(request.args.get('page'))
        per_page = int(request.args.get('per_page'))
        query = select(Books)
        books = db.paginate(query, page=page, per_page=per_page) # Handles out pagination
        print("Page and per page")
        print(jsonify(books))
        return books_schema.jsonify(books), 200
    except: # Defaulting to our regular if they don't send a page or page number  
        books = db.session.query(Books).all()
        print("Default")
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

# Get Popular Books
@books_bp.route('/popularity', methods=['GET'])
def get_popular_books():
    
    books = db.session.query(Books).all() # Grabbing all books
    
    # Sort books list base off of how many loans they've been apart of
    books.sort(key= lambda book: len(book.loans), reverse=True) # Reversing to get the most popular books first
    
    output = []
    for book in books[:5]: # For each individual book
        book_format = {
            "book": book_schema.dump(book), # translate the book to json
            "readers": len(book.loans) # add the amount of readers
        }
        output.append(book_format) # append this dictionary to an output list
        
    return jsonify(output), 200 #jsonify the output list

# Search for a book based on the title or author
@books_bp.route('/search', methods=['GET'])
def search_book():
    title = request.args.get('title')  # Accessing the query parameters from the URL
    author = request.args.get('author')  # Accessing the query parameters from the URL
    
    if title:
        books = db.session.query(Books).where(Books.title.like(f'%{title}%')).all()
    elif author:
        books = db.session.query(Books).where(Books.author.like(f'%{author}%')).all()
    
    return books_schema.jsonify(books), 200