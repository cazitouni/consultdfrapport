from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from decouple import config

import valkey
import time

valkey_client = valkey.Valkey(host=config('VALKEY_HOST'), port=6379)

RATE_LIMIT = int(config('RATE_LIMIT'))
PERIOD = int(config('PERIOD'))

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            user_id = self.get_user_id(request)
            if not user_id:
                return await call_next(request)
            current_time = int(time.time())
            key = f"rate_limit:{user_id}:{current_time // PERIOD}"
            current_count = valkey_client.incr(key)
            if current_count == 1:
                valkey_client.expire(key, PERIOD)
            if current_count > RATE_LIMIT:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            response = await call_next(request)
            return response
        except HTTPException as exc:
            return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    def get_user_id(self, request: Request):
        x_forwarded_for = request.headers.get('X-Forwarded-For')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.client.host
        return ip
