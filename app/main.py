from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routes import router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "AI-powered comic story creator "
        "using Gemini and image generation."
    ),
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(
            settings.STATIC_DIR
        )
    ),
    name="static",
)


app.include_router(
    router
)


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }