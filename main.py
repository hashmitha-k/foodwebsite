from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_tables
from routers import auth_router, users_router, recipes_router, favorites_router

app = FastAPI(title="Recipe App API")

# ─── ALLOW YOUR HTML FILES TO CALL THIS API ──────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # Change "*" to your actual domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── CREATE DATABASE TABLES ON STARTUP ───────────────────────────────
@app.on_event("startup")
def startup():
    create_tables()

# ─── REGISTER ALL ROUTERS ────────────────────────────────────────────
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(recipes_router.router)
app.include_router(favorites_router.router)

@app.get("/")
def root():
    return {"message": "Recipe App API is running!"}
