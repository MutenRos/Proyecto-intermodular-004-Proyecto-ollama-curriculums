#!/usr/bin/env python3
import argparse
import pathlib
import sys
import time
import requests
from textwrap import dedent

# ---------------------------------------------------------
# ⭐ AQUI defines el nombre del archivo Markdown
# ---------------------------------------------------------
ARCHIVO_MD = "CV José Vicente Carratalá Sánchis.md"  # <-- cámbialo por el archivo que quieras
MODELO_DEFECTO = "qwen2.5:3b-instruct"
HOST_DEFECTO = "http://localhost:11434"
# ---------------------------------------------------------


def resumir_cv(
    ruta_archivo: str,
    modelo: str = MODELO_DEFECTO,
    host: str = HOST_DEFECTO
) -> str:
    """
    Lee un CV en Markdown, lo envía a Ollama (endpoint /api/generate)
    y devuelve un resumen profesional en español.
    """

    # Leer el archivo Markdown
    ruta = pathlib.Path(ruta_archivo)
    if not ruta.is_file():
        print(f"Error: no se encontró el archivo '{ruta_archivo}'", file=sys.stderr)
        sys.exit(1)

    contenido_md = ruta.read_text(encoding="utf-8")
    print(f"CV cargado: {len(contenido_md)} caracteres desde '{ruta_archivo}'")

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

    print(f"Enviando a Ollama ({modelo}) en {host}...")
    inicio = time.time()

    try:
        response = requests.post(url, json=payload, timeout=600)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        print(f"Error: no se pudo conectar con Ollama en {host}.", file=sys.stderr)
        print("Asegúrate de que Ollama está ejecutándose.", file=sys.stderr)
        sys.exit(1)
    except requests.exceptions.Timeout:
        print("Error: la petición a Ollama tardó demasiado.", file=sys.stderr)
        sys.exit(1)
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
    duracion = time.time() - inicio
    print(f"Respuesta recibida en {duracion:.1f} segundos")

    # En /api/generate, el texto viene en data["response"]
    try:
        return data["response"].strip()
    except (KeyError, TypeError):
        print("Respuesta inesperada de Ollama:", file=sys.stderr)
        print(data, file=sys.stderr)
        sys.exit(1)


def main():
    # Permitir pasar archivo por línea de comandos
    parser = argparse.ArgumentParser(
        description="Resume un CV en Markdown usando Ollama"
    )
    parser.add_argument(
        "archivo", nargs="?", default=ARCHIVO_MD,
        help=f"Ruta al archivo Markdown (por defecto: {ARCHIVO_MD})"
    )
    parser.add_argument(
        "--modelo", default=MODELO_DEFECTO,
        help=f"Modelo de Ollama a usar (por defecto: {MODELO_DEFECTO})"
    )
    args = parser.parse_args()

    resumen = resumir_cv(args.archivo, modelo=args.modelo)
    print("\n" + "="*60)
    print("RESUMEN DEL CV")
    print("="*60)
    print(resumen)


if __name__ == "__main__":
    main()

