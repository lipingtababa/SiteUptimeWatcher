from random import random
from fastapi import FastAPI, Response, status
from fastapi.requests import Request
import uvicorn

app = FastAPI()

@app.get("/{full_path:path}")
async def catch_all(request: Request):
    rand_val = random()
    if rand_val < 0.1:
        return Response(content="SERVER ERROR", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    elif rand_val < 0.2:
        return Response(content="NOT FOUND", status_code=status.HTTP_404_NOT_FOUND)
    else:
        return "You are always welcome!"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")

