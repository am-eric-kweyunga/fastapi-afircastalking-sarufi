from fastapi import FastAPI
from src.config.settings import settings

# API endpoints
from src.app.api.registration.endpoint import router as registration_router
from src.app.api.orders.endpoints import router as orders_router

app = FastAPI(
    title=settings.NAME,
    version=settings.VERSION,
    debug=settings.DEBUG,
    docs_url="/",
)

app.include_router(registration_router)
app.include_router(orders_router)

