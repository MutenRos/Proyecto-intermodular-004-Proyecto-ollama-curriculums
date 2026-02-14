import os
import sys
from pypdf import PdfReader
from markdownify import markdownify as md


def pdf_to_md(path_pdf, path_md):
    """Convierte un archivo PDF a formato Markdown.
    
    Extrae el texto de cada página del PDF y lo convierte
    a Markdown usando la librería markdownify.
    
    Args:
        path_pdf: Ruta al archivo PDF de entrada.
        path_md:  Ruta donde se guardará el archivo Markdown.
    
    Returns:
        El texto convertido a Markdown.
    """
    # Comprobar que el archivo PDF existe
    if not os.path.isfile(path_pdf):
        print(f"Error: no se encontró el archivo '{path_pdf}'")
        sys.exit(1)

    reader = PdfReader(path_pdf)
    full_text = ""

    for i, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        full_text += text + "\n\n"
        print(f"Página {i}/{len(reader.pages)} extraída")

    # Convertir texto a Markdown (markdownify trabaja mejor con HTML,
    # pero en textos normales también funciona)
    md_text = md(full_text)

    with open(path_md, "w", encoding="utf-8") as f:
        f.write(md_text)

    print(f"Archivo guardado: {path_md} ({len(md_text)} caracteres)")
    return md_text


if __name__ == "__main__":
    pdf_to_md(
        "CV José Vicente Carratalá Sánchis.pdf",
        "CV José Vicente Carratalá Sánchis.md"
    )

