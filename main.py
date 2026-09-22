from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from routes.user import router as user_router
from routes.auth import router as auth_router
from routes.ticket import router as ticket_router
from models.base import Base
from db.db import engine



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173","https://civichelpfrontend.vercel.app","https://civichelp.towhidur-rahman-abed.me"],       
    allow_credentials=True,      
    allow_methods=["*"],         
    allow_headers=["*"],       
)



# create sqlite db
Base.metadata.create_all(bind=engine)

# static files
app.mount("/static", StaticFiles(directory="static"), name="static")

v1_router = APIRouter(prefix="/v1/api")
app.include_router(v1_router)
v1_router.include_router(user_router)
v1_router.include_router(auth_router)
v1_router.include_router(ticket_router)
