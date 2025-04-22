#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" This is the test server that we are going to monitor."""

import random
import asyncio
from fastapi import FastAPI, Response, status
from fastapi.requests import Request
import uvicorn

app = FastAPI()

@app.get("/{full_path:path}")
async def catch_all(_: Request):
    """We ignore any input and return a random response."""
    rand_val = random.randint(0, 100)

    # 20% chance of high latency
    if rand_val % 5 == 0:
        await asyncio.sleep(1)
    else:
        await asyncio.sleep(0.01)

    if rand_val <= 10:
        return Response(content="SERVER ERROR", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    if rand_val <= 20:
        return Response(content="NOT FOUND", status_code=status.HTTP_404_NOT_FOUND)
    return "You are always welcome!"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="debug")
