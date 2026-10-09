import os
import re
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .config import settings


def _safe_filename(text: str) -> str:
    text = text.lower().strip()

    text = re.sub(
        r"[^a-z0-9]+",
        "_",
        text,
    )

    text = text.strip("_")

    if not text:
        text = "panel"

    return text[:80]


def _placeholder_image(
    prompt: str,
    output_path: Path,
):
    image = Image.new(
        "RGB",
        (
            settings.IMAGE_WIDTH,
            settings.IMAGE_HEIGHT,
        ),
        "white",
    )

    draw = ImageDraw.Draw(image)

    title = "ComicCraft"

    draw.text(
        (40, 40),
        title,
        fill="black",
    )

    text = prompt[:500]

    draw.multiline_text(
        (40, 120),
        text,
        fill="black",
        spacing=8,
    )

    image.save(output_path)


def _generate_huggingface(
    prompt: str,
):
    if not settings.HF_TOKEN:
        raise RuntimeError(
            "HF_TOKEN is missing. "
            "Add it to your .env file."
        )

    from huggingface_hub import InferenceClient

    client = InferenceClient(
        provider="auto",
        api_key=settings.HF_TOKEN,
    )

    image = client.text_to_image(
        prompt=prompt,
        model=settings.HF_IMAGE_MODEL,
    )

    return image


def _generate_local(
    prompt: str,
):
    try:
        import importlib

        torch = importlib.import_module("torch")
        diffusers = importlib.import_module("diffusers")
        StableDiffusionPipeline = diffusers.StableDiffusionPipeline
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "Local image generation requires the optional dependencies "
            "'torch' and 'diffusers'. Install them to use "
            "IMAGE_BACKEND='local'."
        ) from exc

    device = (
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    pipe = StableDiffusionPipeline.from_pretrained(
        settings.LOCAL_IMAGE_MODEL,
        torch_dtype=(
            torch.float16
            if device == "cuda"
            else torch.float32
        ),
    )

    pipe = pipe.to(device)

    result = pipe(
        prompt,
        height=settings.IMAGE_HEIGHT,
        width=settings.IMAGE_WIDTH,
    )

    return result.images[0]


def generate_image(
    prompt: str,
    panel_number: int | None = None,
) -> str:

    panel_number = panel_number or 1

    filename = (
        f"panel_{panel_number}_"
        f"{_safe_filename(prompt)}_"
        f"{uuid.uuid4().hex[:8]}.png"
    )

    output_path = (
        settings.PANEL_DIR / filename
    )

    enhanced_prompt = f"""
Comic book illustration.

{prompt}

Visual requirements:
- cinematic composition
- clear subject
- expressive characters
- detailed environment
- strong storytelling
- clean comic illustration
- no watermark
- no text
- no captions
- no speech bubbles
"""

    backend = settings.IMAGE_BACKEND

    if backend == "placeholder":
        _placeholder_image(
            enhanced_prompt,
            output_path,
        )

    elif backend == "hf":
        image = _generate_huggingface(
            enhanced_prompt
        )

        image.save(output_path)

    elif backend == "local":
        image = _generate_local(
            enhanced_prompt
        )

        image.save(output_path)

    else:
        raise RuntimeError(
            f"Unknown IMAGE_BACKEND: {backend}"
        )

    return str(output_path)
fal_key = os.getenv("FAL_KEY")