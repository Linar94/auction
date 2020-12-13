from fastapi import FastAPI, APIRouter

from .db_utils import db
from .auth.views import router as auth_router
from .auction.views import router as auction_router
from .auction.watcher import watch_auction


def include_routers(application):
    api_router = APIRouter()
    api_router.include_router(auth_router)
    api_router.include_router(auction_router)
    application.include_router(api_router)


def get_app():
    _app = FastAPI(
        title="Auction API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json"
    )
    db.init_app(_app)
    include_routers(_app)
    watch_auction()
    return _app


app = get_app()

