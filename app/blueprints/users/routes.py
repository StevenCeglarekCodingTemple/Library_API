from app.blueprints.users import users_bp
from .schemas import user_schema, users_schema
from flask import request, jsonify
from sqlalchemy import select
from marshmallow import ValidationError
from app.models import Users, db
from app.extensions import limiter, cache
from app.utils.util import encode_token, token_required


@users_bp.route('/login', methods=['POST'])
def login():
    try:
        credentials = request.json
        username = credentials['username']
        password = credentials['password']
    except KeyError:
        return jsonify({'messages': 'Invalid payload, expecting username and password'})
    
    query = select(Users).where(Users.username == username)
    user = db.session.execute(query).scalar_one_or_none() # Query user table for a user with this username
    
    if user and user.password == password:
        auth_token = encode_token(user.id)
        
        response = {
            'status': 'success',
            'message': 'Successfully Logged in',
            'auth_token': auth_token
        }
        
        return jsonify(response), 200
    else:
        return jsonify({'messages': 'Invalid username or password'})

#CREATE USER ROUTE
@users_bp.route('', methods=['POST']) #route servers as the trigger for the function below.
@limiter.limit("3 per hour") # A client can only attempt to make 3 users per hour
def create_user():
    try:
        data = user_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400 #Returning the error as a response so my client can see whats wrong.
    

    new_user = Users(**data) #Creating User object
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user), 201

#Read Users
@users_bp.route('', methods=['GET']) #Endpoint to get user information
@cache.cached(timeout=60)
def read_users():
    users = db.session.query(Users).all()
    return users_schema.jsonify(users), 200

#Read Individual User - Using a Dynamic Endpoint
@users_bp.route('<int:user_id>', methods=['GET'])
def read_user(user_id):
    user = db.session.get(Users, user_id)
    return user_schema.jsonify(user), 200

#Delete a User
@users_bp.route('', methods=['DELETE'])
@token_required
def delete_user(user_id):
    user = db.session.get(Users, user_id)
    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": f"Successfully deleted user {user_id}"}), 200

#Update a User
@users_bp.route('<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = db.session.get(Users, user_id) #Query for our user to update

    if not user: #Checking if I got a user
        return jsonify({"message": "user not found"}), 404  #if not return error message
    
    try:
        user_data = user_schema.load(request.json) #Validating updates
    except ValidationError as e:
        return jsonify({"message": e.messages}), 400
    
    for key, value in user_data.items(): #Looping over attributes and values from user data dictionary
        setattr(user, key, value) # setting Object, Attribute, Value to replace

    db.session.commit()
    return user_schema.jsonify(user), 200