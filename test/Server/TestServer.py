#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
from fastapi import FastAPI, Response, status
from fastapi.requests import Request
import uvicorn
import asyncio

app = FastAPI()

@app.get("/{full_path:path}")
async def catch_all(request: Request):
    rand_val = random.randint(0, 100)

    # 20% chance of high latency
    if rand_val % 5 == 0:
        await asyncio.sleep(1)

    if rand_val <= 10:
        return Response(content="SERVER ERROR", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif rand_val <= 20:
        return Response(content="NOT FOUND", status_code=status.HTTP_404_NOT_FOUND)
    else:
        return "You are always welcome!"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
