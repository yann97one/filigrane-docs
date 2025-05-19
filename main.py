import io
import math
import os

from PyPDF2 import PdfFileReader, PdfFileWriter, PdfReader, PdfWriter
from fastapi import FastAPI, Request, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from reportlab.lib.colors import Color, black

from reportlab.lib.pagesizes import letter, landscape, A4
from reportlab.pdfgen import canvas

app = FastAPI()

app.mount("/templates", StaticFiles(directory="templates"), name="templates")


templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html",
    )


async def save_uploaded_file(path: str,file_to_upload: File()):
    with open(path, "wb") as f:
        f.write(await file_to_upload.read())


async def delete_old_file(path: str):
    try:
        if os.path.exists(path=path):
            os.remove(path)
            print(f"Fichier supprimé : {path}")
        else:
            print(f"Le fichier n'existe pas : {path}")
    except Exception as e:
        print(f"Erreur lors de la suppression du fichier {path} : {e}")


def create_watermark(text: str, page_size=A4):
    # Dimensions de la page
    width, height = page_size
    diagonal_length = math.sqrt(width ** 2 + height ** 2)

    # Création du canvas
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=page_size)

    # Configuration du texte du filigrane
    can.setFont("Helvetica-Bold", 80)  # Taille du texte
    can.setFillColor(black)

    # Placement du texte en diagonale
    can.saveState()
    # Centre du document pour la rotation
    can.translate(0, 0)
    can.rotate(45)

    # Calcul du positionnement pour commencer en bas à gauche
    x_offset = -0.2 * diagonal_length  # Légèrement en dehors pour couvrir les marges
    y_offset = 0.1 * diagonal_length
    can.drawString(x_offset, y_offset, text)

    can.restoreState()
    can.save()
    packet.seek(0)
    return packet

@app.post("/filigrane", response_class=HTMLResponse)
async def filigrane_doc(request: Request, file_to_filigrane: UploadFile = File(...)):
    # Sauvegarde du fichier uploadé
    file_path = f"uploads/{file_to_filigrane.filename}"
    await save_uploaded_file(path=file_path,file_to_upload=file_to_filigrane)

    packet = create_watermark("RESERVEE A LA LOCATION IMMOBILIERE")

    # Lecture des PDF
    new_pdf = PdfReader(packet)
    existing_pdf = PdfReader(file_path)
    output_pdf = PdfWriter()

    # Application du filigrane à chaque page
    watermark_page = new_pdf.pages[0]  # La première page du PDF de filigrane

    for page in existing_pdf.pages:
        # Fusionne la page avec le filigrane
        page.merge_page(watermark_page)
        output_pdf.add_page(page)

    # Sauvegarde du fichier filigrané
    output_file_path = f"uploads/filigrane_{file_to_filigrane.filename}"
    with open(output_file_path, "wb") as output_stream:
        output_pdf.write(output_stream)

    print(f"PDF filigrané sauvegardé sous : {output_file_path}")
    await delete_old_file(path=file_path)
    return templates.TemplateResponse("index.html", {"request": request})
