from fastapi import FastAPI
from mangum import Mangum
from api_v1.api import router as api_router

app = FastAPI(
    title="My Awesome FastAPI app",
    description="This is super fancy, with auto docs and everything!",
    version="0.1.0",
)


@app.get("/ping", name="Healthcheck", tags=["Healthcheck"])
async def healthcheck():
    return {"Success": "Pong!"}


app.include_router(api_router, prefix="/api/v1")

handler = Mangum(app)