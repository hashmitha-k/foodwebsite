from sqlalchemy import create_engine, Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

# SQLite database - creates a file called recipes.db in the same folder
DATABASE_URL = "sqlite:///./recipes.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


# ─── DATABASE TABLES ────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id            = Column(Integer, primary_key=True, index=True)
    username      = Column(String, unique=True, nullable=False)
    email         = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)

    recipes       = relationship("Recipe", back_populates="owner")
    favorites     = relationship("Favorite", back_populates="user")


class Recipe(Base):
    __tablename__ = "recipes"

    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, nullable=False)
    description = Column(Text)
    ingredients = Column(Text, nullable=False)   # stored as plain text / JSON string
    steps       = Column(Text, nullable=False)   # stored as plain text / JSON string
    image_url   = Column(String)
    created_at  = Column(DateTime, default=datetime.utcnow)
    owner_id    = Column(Integer, ForeignKey("users.id"))

    owner       = relationship("User", back_populates="recipes")
    favorited_by = relationship("Favorite", back_populates="recipe")


class Favorite(Base):
    __tablename__ = "favorites"

    id        = Column(Integer, primary_key=True, index=True)
    user_id   = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    saved_at  = Column(DateTime, default=datetime.utcnow)

    user      = relationship("User", back_populates="favorites")
    recipe    = relationship("Recipe", back_populates="favorited_by")


# ─── HELPER: get a DB session ────────────────────────────────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Creates all tables when this file is run
def create_tables():
    Base.metadata.create_all(bind=engine)
