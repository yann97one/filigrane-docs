import io
import os

from fastapi import File
from reportlab.lib.colors import Color
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


async def save_uploaded_file(path: str, file_to_upload: File):
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


def create_watermark(text: str, page_size=A4, opacity=0.1, repeat_count=5):
    width, height = page_size
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=page_size)

    # Définir couleur noire avec opacité
    transparent_black = Color(0, 0, 0, alpha=opacity)
    can.setFillColor(transparent_black)
    can.setFont("Helvetica-Bold", 40)

    can.saveState()

    # Se placer au centre de la page
    can.translate(width / 2, height / 2)
    can.rotate(45)

    # Mesure du texte
    text_width = can.stringWidth(text, "Helvetica-Bold", 40)

    # Espacement entre les filigranes
    spacing = 150  # ajustable

    # Répéter autour du centre
    start = -(repeat_count // 2)
    for i in range(start, start + repeat_count):
        x = -text_width / 2
        y = i * spacing
        can.drawString(x, y, text)

    can.restoreState()
    can.save()
    packet.seek(0)
    return packet
