# app/main.py

import shutil
import os
import uuid
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from typing import Optional
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from . import services

# --- Definición de Rutas Absolutas ---
BASE_DIR = Path(__file__).resolve().parent.parent
TEMP_DIR = BASE_DIR / "temp_files"
STATIC_DIR = BASE_DIR / "app" / "static"
AUDIO_RESPONSES_DIR = STATIC_DIR / "audio_responses"

# --- Configuración de la App ---
app = FastAPI(title="Etau Inc. Intelligent Support API")

# --- Middleware de CORS ---
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Crear Directorios al Iniciar ---
TEMP_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_RESPONSES_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# --- FUNCIÓN AUXILIAR REFACTORIZADA ---
# CAMBIO CLAVE: Ahora recibe image_path como un string, no como un UploadFile.
async def process_request(query: str, request: Request, image_path: Optional[str] = None):
    """Función central que solo se ocupa de la lógica de IA, no de los archivos."""
    
    # 1. Generar respuesta técnica usando las rutas de archivo
    text_response = services.generate_intelligent_answer(query, image_path)
    
    # 2. Generar audio
    base_url = str(request.base_url)
    audio_url = services.convert_text_to_speech(text_response, base_url)

    return {"text_response": text_response, "audio_url": audio_url}


# --- ENDPOINTS DE LA API (ACTUALIZADOS) ---

@app.post("/support", summary="Soporte por Texto e Imagen")
async def handle_text_support(request: Request, text_query: str = Form(...), image: Optional[UploadFile] = File(None)):
    """Este endpoint ahora también guarda el archivo de imagen inmediatamente."""
    temp_image_path = None
    try:
        if image and image.filename:
            # Guardamos la imagen inmediatamente al recibirla
            temp_image_path = TEMP_DIR / f"{uuid.uuid4()}_{image.filename}"
            contents = await image.read()
            with open(temp_image_path, "wb") as buffer:
                buffer.write(contents)
        
        # Llamamos a la función auxiliar con la RUTA de la imagen
        return await process_request(text_query, request, str(temp_image_path) if temp_image_path else None)
    
    finally:
        # Limpiamos el archivo temporal de la imagen
        if temp_image_path and temp_image_path.exists():
            os.remove(temp_image_path)


@app.post("/support/audio", summary="Soporte por Audio e Imagen")
async def handle_audio_support(request: Request, audio: UploadFile = File(...), image: Optional[UploadFile] = File(None)):
    """Este endpoint ahora guarda AMBOS archivos inmediatamente."""
    
    temp_audio_path = None
    temp_image_path = None
    
    try:
        # Guardamos y procesamos el audio
        temp_audio_path = TEMP_DIR / f"{uuid.uuid4()}_{audio.filename}"
        contents = await audio.read()
        with open(temp_audio_path, "wb") as buffer:
            buffer.write(contents)
            
        # Guardamos la imagen primero (si existe)
        if image and image.filename:
            temp_image_path = TEMP_DIR / f"{uuid.uuid4()}_{image.filename}"
            contentsImg = await image.read()
            with open(temp_image_path, "wb") as buffer:
                buffer.write(contentsImg)

        transcribed_query = services.transcribe_audio(str(temp_audio_path))
        
        if not transcribed_query.strip():
            raise HTTPException(status_code=400, detail="El audio está vacío o no se pudo transcribir.")
        
        # Llamamos a la función auxiliar con la RUTA de la imagen
        return await process_request(transcribed_query, request, str(temp_image_path) if temp_image_path else None)

    finally:
        # Limpiamos AMBOS archivos temporales
        if temp_audio_path and temp_audio_path.exists():
            os.remove(temp_audio_path)
        if temp_image_path and temp_image_path.exists():
            os.remove(temp_image_path)


@app.get("/", summary="Endpoint de Bienvenida")
def read_root():
    return {"message": "Bienvenido a la API de Soporte Inteligente de Etau Inc."}