from fastapi import FastAPI, Request, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles


from core.templates import templates
from router import filigrane

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(filigrane.router, tags=["filigrane"], prefix="/filigrane")

cards_data = [
    {
        "title": "Ajoutez un filigrane",
        "description": "Transformez vos PDF avec un watermark personnalisé.",
        "linkTo": "/filigrane",
        "icon": "file.svg",
    },
]


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "cards_data": cards_data}
    )
