#!/usr/bin/env python3
import pathlib
import sys
import requests
from textwrap import dedent

# ---------------------------------------------------------
# ⭐ AQUÍ defines el nombre del archivo Markdown
# ---------------------------------------------------------
ARCHIVO_MD = "CV José Vicente Carratalá Sánchis.md"  # <-- cámbialo por el archivo que quieras
# ---------------------------------------------------------


def resumir_cv(
    ruta_archivo: str,
    modelo: str = "qwen2.5:3b-instruct",     # <-- sin espacio al final
    host: str = "http://localhost:11434"
) -> str:
    """
    Lee un CV en Markdown, lo envía a Ollama (endpoint /api/generate)
    y devuelve un resumen profesional en español.
    """

    # Leer el archivo Markdown
    contenido_md = pathlib.Path(ruta_archivo).read_text(encoding="utf-8")

    # Prompt en español
    prompt = dedent(
        f"""
        Eres un experto en selección de personal y redacción de perfiles profesionales.

        Recibirás un currículum en formato Markdown.
        
        Tu tarea:
        - Leer el CV cuidadosamente.
        - Identificar habilidades clave, tecnologías, experiencia relevante y logros.
        - Escribir un resumen profesional conciso en tercera persona.
        - Extensión orientativa: 7–10 líneas (máximo ~200 palabras).
        - Estilo profesional, claro y neutro.
        - No repitas listas del CV; sintetiza y destaca aportes de valor.
        - El resultado debe estar en español.
        
        -Importante: Emite una opinion acerca de si el perfil es valido o no es válido para el puesto de trabajo: profesor de ciclos formativos de formación profesional.

        CV (Markdown):
        ---
        {contenido_md}
        ---
        """
    ).strip()

    # Igual que en tu PHP: /api/generate con "prompt"
    url = f"{host}/api/generate"
    payload = {
        "model": modelo.strip(),   # strip() por seguridad
        "prompt": prompt,
        "stream": False,
    }

    try:
        response = requests.post(url, json=payload, timeout=600)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error al contactar con Ollama en {url}: {e}", file=sys.stderr)
        # Si hay cuerpo de respuesta, lo mostramos para depurar
        if 'response' in locals() and response is not None:
            try:
                print("Cuerpo devuelto por el servidor:", file=sys.stderr)
                print(response.text, file=sys.stderr)
            except Exception:
                pass
        sys.exit(1)

    data = response.json()

    # En /api/generate, el texto viene en data["response"]
    try:
        return data["response"].strip()
    except (KeyError, TypeError):
        print("Respuesta inesperada de Ollama:", file=sys.stderr)
        print(data, file=sys.stderr)
        sys.exit(1)


def main():
    resumen = resumir_cv(ARCHIVO_MD)
    print(resumen)


if __name__ == "__main__":
    main()

