from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

# create  base class for our models
class Base(DeclarativeBase):
    pass

# Instantiate your SQLAlchemy database

db = SQLAlchemy(model_class = Base)
ma = Marshmallow()

db.init_app(app)
ma.init_app(app)

class Member(Base):
    __tablename__ = 'members'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    email: Mapped[str] = mapped_column(db.String(360), nullable=False, unique=True)
    dob: Mapped[datetime] = mapped_column(db.DateTime)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    
    loans: Mapped[list['Loan']] = db.relationship('Loan', back_populates='member')
    
loan_book = db.Table(
    'loan_book',
    Base.metadata,
    db.Column('loan_id', db.ForeignKey('loans.id')),
    db.Column('book_id', db.ForeignKey('books.id'))
)

class Loan(Base):
    __tablename__ = 'loans'

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_date: Mapped[datetime] = mapped_column(db.DateTime)
    member_id: Mapped[int] = mapped_column(db.ForeignKey('members.id'))
    
    member: Mapped['Member'] = db.relationship('Member', back_populates='loans')
    books: Mapped[list['Book']] = db.relationship('Book', secondary=loan_book, back_populates='loans')
    
class Book(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    author: Mapped[str] = mapped_column(db.String(255), nullable=False)
    genre: Mapped[str] = mapped_column(db.String(255), nullable=False)
    title: Mapped[str] = mapped_column(db.String(255), nullable=False)
    desc: Mapped[str] = mapped_column(db.String(255), nullable=False)
    
    loans: Mapped[list['Loan']] = db.relationship('Loan', secondary=loan_book, back_populates='books')
    

class MemberSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Member
        
member_schema = MemberSchema()
members_schema = MemberSchema(many=True)

class LoanSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Loan
        
loan_schema = LoanSchema()
loans_schema = LoanSchema(many=True)

class BookSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Book
        
book_schema = BookSchema()
books_schema = BookSchema(many=True)


# API ENDPOINTS

#-------------------- CREATE ---------------------

@app.route("/members", methods=['POST'])
def create_member():
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    query = select(Member).where(Member.email == member_data['email']) # Checking our db for a member with this email
    existing_member = db.session.execute(query).scalars().all()
    if existing_member:
        return jsonify({"error": "Email already associated with an account"}), 400
    
    new_member = Member(**member_data)
    db.session.add(new_member)
    db.session.commit()
    return member_schema.jsonify(new_member), 201
    
#------------------ GET All -------------------------

@app.route("/members", methods=['GET'])
def get_members():
    query = select(Member)
    members = db.session.execute(query).scalars().all()

    return members_schema.jsonify(members)
    
    
#------------------ Get One ----------------------

@app.route("/members/<int:member_id>", methods=['GET'])
def get_member(member_id):
    member = db.session.get(Member, member_id)
    
    if member:
        return member_schema.jsonify(member), 200
    return jsonify({'error': 'Member not found'}), 404

#--------------- Update ---------------------

@app.route("/members/<int:member_id>", methods=['PUT'])
def update_member(member_id):
    member = db.session.get(Member, member_id)
    
    if not member:
        return jsonify({'error': "Member not found"}), 404
    
    try:
        member_data = member_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400
    
    for key, value in member_data.items():
        setattr(member, key, value)
    
    db.session.commit()
    return member_schema.jsonify(member), 200


#--------------- Delete -------------

@app.route("/members/<int:member_id>", methods=['DELETE'])
def delete_member(member_id):
    member = db.session.get(Member, member_id)
    
    if not member:
        return jsonify({'error': "Member not found"})
    
    db.session.delete(member)
    db.session.commit()
    return jsonify({"message": f"Member id: {member_id}, Member name: {member.name} successfully deleted"})
    
# Create the table
with app.app_context():
    db.create_all()
    
app.run(debug=True, port=5001)