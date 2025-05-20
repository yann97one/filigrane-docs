from fastapi import APIRouter, File, Request, UploadFile
from fastapi.responses import HTMLResponse
from PyPDF3 import PdfFileReader, PdfFileWriter
from fastapi.responses import HTMLResponse
from main import templates

from utils.docs_utils import create_watermark, delete_old_file, save_uploaded_file


router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def filigrane(request: Request):
    return templates.TemplateResponse("filigrane_form.html", {"request": request})


@router.post("/", response_class=HTMLResponse)
async def filigrane_doc(request: Request, file_to_filigrane: UploadFile = File(...)):
    # Sauvegarde du fichier uploadé
    file_path = f"uploads/{file_to_filigrane.filename}"
    await save_uploaded_file(path=file_path, file_to_upload=file_to_filigrane)

    packet = create_watermark("RESERVEE A LA LOCATION IMMOBILIERE")

    # Lecture des PDF
    new_pdf = PdfFileReader(packet)
    existing_pdf = PdfFileReader(file_path)
    output_pdf = PdfFileWriter()

    watermark_page = new_pdf.pages[0]  # La première page du PDF de filigrane

    for page in existing_pdf.pages:
        # Fusionne la page avec le filigrane
        page.mergePage(watermark_page)
        output_pdf.addPage(page)

    # Sauvegarde du fichier filigrané
    output_file_path = f"uploads/filigrane_{file_to_filigrane.filename}"
    with open(output_file_path, "wb") as output_stream:
        output_pdf.write(output_stream)

    print(f"PDF filigrané sauvegardé sous : {output_file_path}")
    await delete_old_file(path=file_path)
    return templates.TemplateResponse("index.html", {"request": request})
