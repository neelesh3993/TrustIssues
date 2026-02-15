import time
from fastapi import Request


async def logging_middleware(request: Request, call_next):
    start_time = time.time()

    response = await call_next(request)

    duration = round((time.time() - start_time) * 1000, 2)

    print(f"[LOG] {request.method} {request.url.path} - {duration} ms")

    return response
