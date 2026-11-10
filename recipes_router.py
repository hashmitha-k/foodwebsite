from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from database import get_db, Recipe, User
from auth import get_current_user

router = APIRouter(prefix="/recipes", tags=["Recipes"])


# ─── SCHEMAS ─────────────────────────────────────────────────────────

class RecipeCreate(BaseModel):
    title:       str
    description: Optional[str] = None
    ingredients: str           # e.g. "2 eggs, 1 cup flour, ..."
    steps:       str           # e.g. "1. Mix eggs. 2. Add flour..."
    image_url:   Optional[str] = None

class RecipeUpdate(BaseModel):
    title:       Optional[str] = None
    description: Optional[str] = None
    ingredients: Optional[str] = None
    steps:       Optional[str] = None
    image_url:   Optional[str] = None

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


# ─── GET ALL RECIPES (anyone can view) ───────────────────────────────

@router.get("/", response_model=List[RecipeOut])
def get_all_recipes(db: Session = Depends(get_db)):
    return db.query(Recipe).all()


# ─── GET A SINGLE RECIPE ─────────────────────────────────────────────

@router.get("/{recipe_id}", response_model=RecipeOut)
def get_recipe(recipe_id: int, db: Session = Depends(get_db)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found.")
    return recipe


# ─── GET MY RECIPES ──────────────────────────────────────────────────

@router.get("/my/recipes", response_model=List[RecipeOut])
def get_my_recipes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Recipe).filter(Recipe.owner_id == current_user.id).all()


# ─── ADD A NEW RECIPE ────────────────────────────────────────────────

@router.post("/", response_model=RecipeOut, status_code=201)
def create_recipe(data: RecipeCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    recipe = Recipe(
        title       = data.title,
        description = data.description,
        ingredients = data.ingredients,
        steps       = data.steps,
        image_url   = data.image_url,
        owner_id    = current_user.id,
    )
    db.add(recipe)
    db.commit()
    db.refresh(recipe)
    return recipe


# ─── UPDATE YOUR RECIPE ──────────────────────────────────────────────

@router.put("/{recipe_id}", response_model=RecipeOut)
def update_recipe(recipe_id: int, data: RecipeUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found.")
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only edit your own recipes.")

    if data.title:       recipe.title       = data.title
    if data.description: recipe.description = data.description
    if data.ingredients: recipe.ingredients = data.ingredients
    if data.steps:       recipe.steps       = data.steps
    if data.image_url:   recipe.image_url   = data.image_url

    db.commit()
    db.refresh(recipe)
    return recipe


# ─── DELETE YOUR RECIPE ──────────────────────────────────────────────

@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found.")
    if recipe.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only delete your own recipes.")

    db.delete(recipe)
    db.commit()
    return {"message": "Recipe deleted."}
