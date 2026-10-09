from pathlib import Path

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)
from fastapi.responses import (
    FileResponse,
    HTMLResponse,
)
from fastapi.templating import Jinja2Templates

from .config import settings
from .exporters import save_pdf
from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .layout_builder import build_comic_layout
from .schemas import PromptRequest


router = APIRouter()

templates = Jinja2Templates(
    directory=str(
        settings.TEMPLATE_DIR
    )
)


def run_comic_pipeline(
    request: PromptRequest,
):
    outline = generate_outline(
        story_prompt=request.story_prompt,
        character_name=request.character_name,
        setting=request.setting,
        tone=request.tone,
        art_style=request.art_style,
    )

    story = generate_story(
        outline=outline,
        story_prompt=request.story_prompt,
        character_name=request.character_name,
        setting=request.setting,
        tone=request.tone,
        art_style=request.art_style,
    )

    image_paths = []

    for panel in story:
        image_path = generate_image(
            prompt=panel.image_prompt,
            panel_number=panel.panel_number,
        )

        image_paths.append(
            image_path
        )

    layout = build_comic_layout(
        panels=story,
        image_paths=image_paths,
    )

    pdf_path = save_pdf(
        layout
    )

    return story, layout, pdf_path


@router.get(
    "/",
    response_class=HTMLResponse,
)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": settings.APP_NAME
        },
    )


@router.post(
    "/generate",
    response_class=HTMLResponse,
)
async def generate_comic(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form(...),
    setting: str = Form(...),
    tone: str = Form(...),
    art_style: str = Form(...),
):

    try:

        comic_request = PromptRequest(
            story_prompt=story_prompt,
            character_name=character_name,
            setting=setting,
            tone=tone,
            art_style=art_style,
        )

        story, layout, pdf_path = (
            run_comic_pipeline(
                comic_request
            )
        )

        pdf_filename = Path(
            pdf_path
        ).name

        return templates.TemplateResponse(
            request=request,
            name="comic_preview.html",
            context={
                "app_name": settings.APP_NAME,
                "panels": layout,
                "pdf_url": (
                    f"/download/{pdf_filename}"
                ),
            },
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={
                "app_name": settings.APP_NAME,
                "error": str(exc),
            },
            status_code=500,
        )


@router.post(
    "/generate-comic/json"
)
async def generate_comic_json(
    payload: PromptRequest,
):

    try:

        story, layout, pdf_path = (
            run_comic_pipeline(
                payload
            )
        )

        pdf_filename = Path(
            pdf_path
        ).name

        return {
            "success": True,
            "message": "Comic generated successfully.",
            "panels": [
                panel.model_dump()
                for panel in story
            ],
            "layout": layout,
            "pdf_url": (
                f"/download/{pdf_filename}"
            ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get(
    "/test-image"
)
async def test_image(
    prompt: str = (
        "A brave fox exploring "
        "an enchanted forest"
    ),
):

    try:

        image_path = generate_image(
            prompt=prompt,
            panel_number=0,
        )

        filename = Path(
            image_path
        ).name

        return {
            "success": True,
            "image_url": (
                f"/static/panels/{filename}"
            ),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )


@router.get(
    "/download/{filename}"
)
async def download_pdf(
    filename: str,
):

    safe_name = Path(
        filename
    ).name

    file_path = (
        settings.EXPORT_DIR
        / safe_name
    )

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="PDF not found.",
        )

    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=safe_name,
    )


@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
async def export_success(
    request: Request,
):
    return templates.TemplateResponse(
        request=request,
        name="export_success.html",
        context={
            "app_name": settings.APP_NAME
        },
    )