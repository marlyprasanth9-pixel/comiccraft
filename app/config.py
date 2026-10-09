import os
from pathlib import Path

from dotenv import load_dotenv


# Project root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env
load_dotenv(BASE_DIR / ".env")


class Settings:
    APP_NAME: str = os.getenv("APP_NAME", "ComicCraft")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

    # Current Gemini model names can be changed from .env
    GEMINI_OUTLINE_MODEL: str = os.getenv(
        "GEMINI_OUTLINE_MODEL",
        "gemini-2.5-flash",
    )

    GEMINI_STORY_MODEL: str = os.getenv(
        "GEMINI_STORY_MODEL",
        "gemini-2.5-pro",
    )

    # Image backend:
    # hf = Hugging Face hosted image generation
    # local = local Diffusers model
    # placeholder = no external image service
    IMAGE_BACKEND: str = os.getenv(
        "IMAGE_BACKEND",
        "hf",
    ).lower()

    HF_TOKEN: str = os.getenv("HF_TOKEN", "")

    HF_IMAGE_MODEL: str = os.getenv(
        "HF_IMAGE_MODEL",
        "stabilityai/stable-diffusion-xl-base-1.0",
    )

    LOCAL_IMAGE_MODEL: str = os.getenv(
        "LOCAL_IMAGE_MODEL",
        "runwayml/stable-diffusion-v1-5",
    )

    NUM_PANELS: int = int(
        os.getenv("NUM_PANELS", "5")
    )

    IMAGE_WIDTH: int = int(
        os.getenv("IMAGE_WIDTH", "768")
    )

    IMAGE_HEIGHT: int = int(
        os.getenv("IMAGE_HEIGHT", "768")
    )

    BASE_DIR: Path = BASE_DIR

    STATIC_DIR: Path = BASE_DIR / "static"

    PANEL_DIR: Path = STATIC_DIR / "panels"

    EXPORT_DIR: Path = BASE_DIR / "exports"

    TEMPLATE_DIR: Path = BASE_DIR / "templates"


settings = Settings()


# Make sure required directories exist
settings.PANEL_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

settings.EXPORT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)
FAL_KEY: str = os.getenv("FAL_KEY", "")