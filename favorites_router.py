from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from typing import Optional
from database import get_db, Favorite, Recipe, User
from auth import get_current_user

router = APIRouter(prefix="/favorites", tags=["Favorites"])


# ─── SCHEMA ──────────────────────────────────────────────────────────

class RecipeOut(BaseModel):
    id:          int
    title:       str
    description: Optional[str]
    ingredients: str
    steps:       str
    image_url:   Optional[str]
    owner_id:    int

    class Config:
        from_attributes = True


# ─── GET MY FAVORITE RECIPES ─────────────────────────────────────────

@router.get("/", response_model=List[RecipeOut])
def get_favorites(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    favs = db.query(Favorite).filter(Favorite.user_id == current_user.id).all()
    return [fav.recipe for fav in favs]


# ─── ADD TO FAVORITES ────────────────────────────────────────────────

@router.post("/{recipe_id}", status_code=201)
def add_favorite(recipe_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found.")

    already = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id).first()
    if already:
        raise HTTPException(status_code=400, detail="Already in favorites.")

    fav = Favorite(user_id=current_user.id, recipe_id=recipe_id)
    db.add(fav)
    db.commit()
    return {"message": f"'{recipe.title}' added to favorites."}


# ─── REMOVE FROM FAVORITES ───────────────────────────────────────────

@router.delete("/{recipe_id}")
def remove_favorite(recipe_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    fav = db.query(Favorite).filter(Favorite.user_id == current_user.id, Favorite.recipe_id == recipe_id).first()
    if not fav:
        raise HTTPException(status_code=404, detail="Recipe not in your favorites.")

    db.delete(fav)
    db.commit()
    return {"message": "Removed from favorites."}
