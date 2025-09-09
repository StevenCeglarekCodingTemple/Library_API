from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

# create  base class for our models
class Base(DeclarativeBase):
    pass

# Instantiate your SQLAlchemy database

db = SQLAlchemy(model_class = Base)

db.init_app(app)

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
    
# Create API Routes Here----
    
# Create the table
with app.app_context():
    db.create_all()
    
app.run()