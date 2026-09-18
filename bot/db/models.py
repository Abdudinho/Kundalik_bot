from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Float, ForeignKey, create_engine
from dotenv import load_dotenv
from os import getenv

load_dotenv()

DATABASE_URL = (
    f"postgresql+psycopg2://{getenv('DB_USER')}:{getenv('DB_PASSWORD')}"
    f"@{getenv('DB_HOST')}:{getenv('DB_PORT')}/{getenv('DB_NAME')}"
)

engine = create_engine(DATABASE_URL)

class Base(DeclarativeBase):
    pass

class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True)
    grade = Column(Integer, nullable=False)   # sinf: 1-11
    letter = Column(String, nullable=False)   # harf: A, B, V ...
    day = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    room = Column(String)                     # xona

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"))

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    username = Column(String)

metadata = Base.metadata
Base.metadata.create_all(engine)