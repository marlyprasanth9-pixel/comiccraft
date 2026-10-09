# ComicCraft

ComicCraft is an AI-powered comic story creator built with FastAPI.

It generates:

- Comic story outlines
- Panel narration
- Character dialogue
- AI-generated illustrations
- Comic previews
- Downloadable PDF comics

## Architecture

Frontend:

- HTML
- CSS
- Jinja2

Backend:

- FastAPI
- Pydantic

AI:

- Google Gemini
- Hugging Face image generation
- Optional local Stable Diffusion

PDF:

- FPDF2

## Project Structure

```text
comiccraft/
│
├── app/
│   ├── main.py
│   ├── routes.py
│   ├── config.py
│   ├── schemas.py
│   ├── gemini_flash.py
│   ├── gemini_pro.py
│   ├── image_generator.py
│   ├── layout_builder.py
│   └── exporters.py
│
├── templates/
├── static/
├── exports/
├── tests/
├── .env
├── requirements.txt
└── README.md