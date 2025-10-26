#!/usr/bin/env python3
"""

Descarga imágenes las redimensiona todas al mismo tamaño con transparencia, y las guarda.

Debes proporcionar el diccionario con nombre → URL/image path.
"""

import os
import io
import requests
from PIL import Image

# --- CONFIG ---
OUTPUT_DIR = "output"
FINAL_SIZE = (250, 400)  # puedes ajustar
TIMEOUT = 15
HEADERS = {"User-Agent": "resizer-downloader/1.0"}
# ---------------

# Diccionario nombre → URL (o ruta) de la imagen frontal

#example:
images = {
    "Python_logo": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1024px-Python-logo-notext.svg.png",
}

def fetch_image(url):
    resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.content

def resize_and_save(image_bytes, out_path):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    img.thumbnail(FINAL_SIZE, Image.LANCZOS)
    # lienzo transparente
    background = Image.new("RGBA", FINAL_SIZE, (0,0,0,0))
    x = (FINAL_SIZE[0] - img.width) // 2
    y = (FINAL_SIZE[1] - img.height) // 2
    background.paste(img, (x,y), img)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    background.save(out_path, format="PNG", optimize=True)

def process_card(name, url):
    print(f"Procesando carta: {name}")
    try:
        b = fetch_image(url)
    except Exception as e:
        print("  Error al descargar:", e)
        return False
    safe = "".join(c if c.isalnum() or c in "_-" else "_" for c in name)
    out = os.path.join(OUTPUT_DIR, f"{safe}.png")
    try:
        resize_and_save(b, out)
    except Exception as e:
        print("  Error al procesar guardar:", e)
        return False
    print("  Guardada:", out)
    return True

def main():
    total = len(images)
    ok = 0
    for nm, url in images.items():
        if process_card(nm, url):
            ok += 1
    print(f"Completadas: {ok}/{total}")

if __name__ == "__main__":
    main()
