from datetime import datetime, timedelta

from fastapi.responses import FileResponse, HTMLResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.templating import templates


class RateLimitingMiddleware(BaseHTTPMiddleware):
    RATE_LIMIT_DURATION = timedelta(minutes=1)
    RATE_LIMIT_REQUESTS = 100

    def __init__(self, app):
        super().__init__(app)
        self.request_counts = {}

    async def dispatch(self, request, call_next):
        client_ip = request.client.host

        request_count, last_request = self.request_counts.get(
            client_ip, (0, datetime.min)
        )

        elapsed_time = datetime.now() - last_request

        if elapsed_time > self.RATE_LIMIT_DURATION:
            request_count = 1
        else:
            if request_count >= self.RATE_LIMIT_REQUESTS:
                return HTMLResponse(
                    "<p style='font-size: 25px;'><b>Слишком много запросов, повторите через 1 минуту...<b></p>"
                )
            request_count += 1

        self.request_counts[client_ip] = (request_count, datetime.now())

        response = await call_next(request)
        return response
