from fastapi import FastAPI
from app.api.user_administration import auth, users, roles, menus, processes, persons, images
from app.core.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from app.exceptions.handlers import register_exception_handlers
from app.api.client_administration.clients import router as clients_router

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

app.include_router(auth.router,      prefix="/api/auth",      tags=["Auth"])
app.include_router(users.router,     prefix="/api/users",     tags=["Users"])
app.include_router(roles.router,     prefix="/api/roles",     tags=["Roles"])
app.include_router(menus.router,     prefix="/api/menus",     tags=["Menus"])
app.include_router(processes.router, prefix="/api/processes", tags=["Processes"])
app.include_router(persons.user_person_router, prefix="/api/users/{user_id}/person", tags=["Persons"])
app.include_router(persons.persons_router, prefix="/api/persons", tags=["Persons"])
# ── Nuevo router de imágenes ─────────────────────────
app.include_router(images.router,
    prefix="/api/images",    tags=["Images"])
app.include_router(
    clients_router,
    prefix="/api/client_administration/clients",
    tags=["clients"]
)

@app.get("/health")
def health():
    return {"status": "ok"}
