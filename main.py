from fastapi import FastAPI
from app.api.user_administration import auth, users, roles, menus, processes, persons, images
from app.core.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from app.exceptions.handlers import register_exception_handlers
from app.api.client_administration.clients import router as clients_router
from app.api.chofer_administration.choferes import router as choferes_router
from app.api.camion_administration.camiones import router as camiones_router
from app.api.servicio_mecanico.talleres      import router as talleres_router
from app.api.servicio_mecanico.tipos_servicio import router as tipos_servicio_router
from app.api.servicio_mecanico.repuestos      import router as repuestos_router
from app.api.servicio_mecanico.servicios      import router as servicios_router


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
app.include_router(
    choferes_router,
    prefix="/api/chofer_administration/choferes",
    tags=["choferes"]
)
app.include_router(
    camiones_router,
    prefix="/api/camion_administration/camiones",
    tags=["camiones"]
)
app.include_router(talleres_router,       prefix="/api/servicio_mecanico/talleres",       tags=["talleres"])
app.include_router(tipos_servicio_router, prefix="/api/servicio_mecanico/tipos_servicio", tags=["tipos_servicio"])
app.include_router(repuestos_router,      prefix="/api/servicio_mecanico/repuestos",      tags=["repuestos"])
app.include_router(servicios_router,      prefix="/api/servicio_mecanico/servicios",      tags=["servicios"])

@app.get("/health")
def health():
    return {"status": "ok"}
