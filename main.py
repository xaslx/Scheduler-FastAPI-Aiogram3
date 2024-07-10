from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from app.routers.auth_router import auth_router
from app.routers.user_router import user_router
from app.routers.main_router import main_router
from app.routers.notification_router import notification_router
from app.routers.not_found_router import not_found
from app.routers.booking_router import booking_router
from app.utils.templating import templates
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from config import settings
from app.models.user_model import User
from app.auth.dependencies import get_current_user
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from middleware import RateLimitingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url(f"redis://{settings.REDIS_HOST}", encoding="utf-8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    yield



app: FastAPI = FastAPI(
    title='Scheduler',
    version='0.1',
    lifespan=lifespan,
)

#пагинация
add_pagination(app)

#роутеры
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(main_router)
app.include_router(not_found)
app.include_router(booking_router)
app.include_router(notification_router)

#мидлвары
#app.add_middleware(HTTPSRedirectMiddleware)  #все запросы должны быть с https / ws
# app.add_middleware(RateLimitingMiddleware)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8000",
    "https://127.0.0.1:8000",
    "http://127.0.0.1:8000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/app/static", StaticFiles(directory="app/static"), "static")


@app.exception_handler(StarletteHTTPException)
async def custom_http_exception_handler(request: Request, exc) -> HTMLResponse:
    return RedirectResponse(url='/error/not_found')

