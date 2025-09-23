from datetime import date, datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Date, String, Table, Column, ForeignKey, DateTime, Float, Integer

# create  base class for our models
class Base(DeclarativeBase):
    pass

#Instatiate your SQLAlchemy database:
db = SQLAlchemy(model_class = Base)

loan_books = db.Table(
    'loan_books',
    Base.metadata,
    db.Column('loan_id', ForeignKey('loans.id')),
    db.Column('book_id', ForeignKey('books.id'))
)


class Users(Base):
    __tablename__ = 'users'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(360), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(120), nullable=False)
    DOB: Mapped[date] = mapped_column(Date, nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    role: Mapped[str] = mapped_column(String(30), nullable=False)

    #One to Many relationship from User to Books
    loans: Mapped[list['Loans']] = relationship('Loans', back_populates='user')
    orders: Mapped[list['Orders']] = relationship('Orders', back_populates='user')
  
  
class Loans(Base):
    __tablename__ = 'loans'

    id: Mapped[int] = mapped_column(primary_key=True)
    loan_date: Mapped[date] = mapped_column(Date, nullable=True)
    deadline: Mapped[date] = mapped_column(Date, nullable=True)
    return_date: Mapped[date] = mapped_column(Date, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)

    #Relationships
    user: Mapped['Users'] = relationship('Users', back_populates='loans')
    books: Mapped[list['Books']] = relationship("Books", secondary=loan_books, back_populates='loans') #Many to Many relationship going through the loan_books table
 

class Books(Base):
    __tablename__ = 'books'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    genre: Mapped[str] = mapped_column(String(360), unique=True, nullable=False)
    age_category: Mapped[str] = mapped_column(String(120), nullable=False)
    publish_date: Mapped[date] = mapped_column(Date, nullable=True)
    author: Mapped[str] = mapped_column(String(500), nullable=True)

    #Relationship
    loans: Mapped[list['Loans']] = relationship('Loans', secondary=loan_books, back_populates='books')
    

class Orders(Base):
    __tablename__ = 'orders'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    order_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(), nullable=False)
    
    user: Mapped['Users'] = relationship('Users', back_populates='orders')
    item_orders: Mapped[list['ItemOrders']] = relationship('ItemOrders', back_populates='order')
    
class Items(Base):
    __tablename__ = 'items'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    item_name: Mapped[str] = mapped_column(String(225), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    
    item_orders: Mapped[list['ItemOrders']] = relationship('ItemOrders', back_populates='item')
    
class ItemOrders(Base):
    __tablename__ = 'item_orders'
    
    id: Mapped[int] = mapped_column(primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey('items.id'), nullable=False)
    order_id: Mapped[int] = mapped_column(ForeignKey('orders.id'), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    order: Mapped['Orders'] = relationship('Orders', back_populates='item_orders')
    item: Mapped['Items'] = relationship('Items', back_populates='item_orders')