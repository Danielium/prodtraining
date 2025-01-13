from fastapi import FastAPI
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()


@app.get("/api/ping", summary='Главная ручка')
async def ping():
    return JSONResponse(content={"status": "ok"}, status_code=200)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
