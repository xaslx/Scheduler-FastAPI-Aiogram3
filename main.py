from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_pagination import add_pagination
from redis_init import redis
import sentry_sdk

from app.auth.dependencies import get_current_user
from app.repository.notification_repo import NotificationRepository
from app.routers.auth_router import auth_router
from app.routers.booking_router import booking_router
from app.routers.main_router import main_router
from app.routers.notification_router import notification_router
from app.routers.user_router import user_router
from app.routers.websocket_router import websocket_router
from app.schemas.notification_schemas import NotificationOut
from app.schemas.user_schema import UserOut
from app.utils.templating import templates
from config import settings
from database import async_session_maker
from logger import logger
from middleware import RateLimitingMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from bot.run import on_startup, handle_web_hook
from app.tasks.apscheduler import scheduler



sentry_sdk.init(
    dsn=settings.dsn,
    traces_sample_rate=1.0,
    profiles_sample_rate=1.0
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    FastAPICache.init(RedisBackend(redis), prefix="cache")
    scheduler.start()
    await on_startup()
    logger.info('Fastapi приложение и Бот запущены')
    yield
    await redis.close()
    scheduler.shutdown()



app: FastAPI = FastAPI(
    title="Scheduler",
    version="0.1",
    lifespan=lifespan,
    docs_url=None,
    redoc_url=None
)


# instrumentator: Instrumentator = Instrumentator(
#     should_group_status_codes=False,
#     excluded_handlers=["metrics"]
# )
# instrumentator.instrument(app).expose(app)

# пагинация
add_pagination(app)

# роутеры
app.add_route(f'/{settings.TOKEN_BOT}', handle_web_hook, methods=["POST"])
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(main_router)
app.include_router(booking_router)
app.include_router(notification_router)
app.include_router(websocket_router)

app.add_middleware(RateLimitingMiddleware)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8000",
    "http://localhost:8000",
    "https://127.0.0.1:8000",
    "http://127.0.0.1:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/app/static", StaticFiles(directory="app/static"), "static")


@app.exception_handler(404)
async def custom_404_handler(request: Request, __) -> HTMLResponse:
    async with async_session_maker() as session:
        user: UserOut = await get_current_user(
            async_db=session, token=request.cookies.get("user_access_token")
        )
        notifications: list[NotificationOut] = (
            await NotificationRepository.find_all_notif(session=session)
        )
    return templates.TemplateResponse(
        request=request,
        name="404.html",
        context={"user": user, "notifications": notifications},
    )