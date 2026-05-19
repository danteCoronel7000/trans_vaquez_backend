from fastapi import FastAPI
from app.api.user_administration import auth, users, roles, menus, processes, persons
from app.core.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from app.exceptions.handlers import register_exception_handlers

app = FastAPI(
    title="Transport API",
    version="1.0.0",
    description="Backend para sistema de transporte de cargas",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(auth.router,      prefix="/api/user_administration/auth",      tags=["Auth"])
app.include_router(users.router,     prefix="/api/user_administration/users",     tags=["Users"])
app.include_router(roles.router,     prefix="/api/user_administration/roles",     tags=["Roles"])
app.include_router(menus.router,     prefix="/api/user_administration/menus",     tags=["Menus"])
app.include_router(processes.router, prefix="/api/user_administration/processes", tags=["Processes"])
app.include_router(persons.user_person_router, prefix="/api/user_administration/users/{user_id}/person", tags=["Persons"])
app.include_router(persons.persons_router, prefix="/api/user_administration/persons", tags=["Persons"])

@app.get("/health")
def health():
    return {"status": "ok"}
