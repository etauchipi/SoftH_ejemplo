# SoftHelp Support API
# SoftHelp Inc.
Ejemplo FastAPI
# 🤖 API de Soporte Inteligente Multimodal

Esta es una API REST multimodal diseñada para actuar como un sistema de soporte técnico inteligente para SoftHelp Inc. La API puede recibir preguntas de usuarios en formato de texto, audio o imagen, procesarlas utilizando un stack de modelos de IA de código abierto, y devolver una respuesta tanto en texto como en audio sintetizado.

El sistema utiliza una arquitectura **RAG (Retrieval-Augmented Generation)** para basar sus respuestas en una base de conocimiento interna (manuales, FAQs, etc.).

---

## ✨ Características Principales

* **Entrada Multimodal:** Acepta peticiones con texto, audio (`.mp3`, `.wav`) e imágenes (`.jpg`, `.png`).
* **Speech-to-Text:** Transcripción de audio de alta precisión utilizando **Whisper**.
* **Análisis de Visión:** Descripción de imágenes y capturas de pantalla mediante el modelo **LLaVA**.
* **Generación Aumentada por Recuperación (RAG):** Búsqueda de contexto en una base de conocimiento vectorial (ChromaDB) para respuestas más precisas y fundamentadas.
* **Generación de Lenguaje Natural:** Creación de respuestas técnicas claras utilizando un LLM local como **Phi-3**.
* **Text-to-Speech:** Conversión de la respuesta de texto a voz utilizando **gTTS**.
* **API Robusta:** Construida con **FastAPI**, garantizando alto rendimiento y una documentación interactiva automática.
* **100% Open Source:** Todo el stack de IA puede correr localmente utilizando **Ollama**.
* **Prompt aumentado:** Crea un prompt aumentado y configurado para generar la respuesta más acertada basado en su contexto **RAG**.

---

## 🛠️ Stack Tecnológico

| Componente | Herramienta |
| :--- | :--- |
| **Framework API** | `FastAPI` |
| **Servidor** | `Uvicorn` |
| **Servidor de Modelos IA** | `Ollama` |
| **LLM de Texto** | `Phi-3` (o `Llama 3`) |
| **LLM de Visión (V2V)**| `LLaVA` |
| **Transcripción (STT)**| `Whisper` (OpenAI) |
| **Síntesis de Voz (TTS)**| `gTTS` |
| **Orquestador RAG** | `LangChain` |
| **Base de Datos Vectorial** | `ChromaDB` |
| **Embeddings** | `SentenceTransformers` |

---

## ⚙️ Configuración e Instalación

### Requisitos Previos

Asegúrate de tener instalado lo siguiente en tu sistema:

1.  **Python 3.8+** y `pip`.
2.  **Ollama:** Sigue la [guía de instalación oficial](https://ollama.com/).
3.  **ffmpeg:** Herramienta esencial para el procesamiento de audio.
    * **Windows (con Chocolatey):** `choco install ffmpeg`
    * **macOS (con Homebrew):** `brew install ffmpeg`
    * **Linux (con apt):** `sudo apt update && sudo apt install ffmpeg`

### Pasos de Instalación

1.  **Clona el repositorio (si aplica):**
    ```bash
    git clone [https://tu-repositorio.git](https://tu-repositorio.git)
    cd nombre-del-proyecto
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    python -m venv .venv
    # En Windows
    .venv\Scripts\activate
    # En macOS/Linux
    source .venv/bin/activate
    ```

3.  **Instala las dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Descarga los modelos de Ollama:**
    ```bash
    ollama pull phi3
    ollama pull llava
    ```

5.  **Prepara la Base de Conocimiento:**
    * Crea una carpeta llamada `knowledge_base` en la raíz del proyecto.
    * Coloca dentro tus archivos `.pdf` y `.txt` (ej: `Manual_Usuario.pdf`, `FAQ.txt`).

---

## ▶️ Ejecución de la Aplicación

1.  **Ingesta de Datos (Ejecutar solo una vez o al cambiar los documentos):**
    Este script procesará los documentos de `knowledge_base/` y los guardará en la base de datos vectorial.
    ```bash
    python ingest.py
    ```

2.  **Inicia el Servidor de la API:**
    Asegúrate de que la aplicación de Ollama esté corriendo en tu sistema. Luego, ejecuta:
    ```bash
    uvicorn app.main:app --reload
    ```
    La API estará disponible en `http://localhost:8000`.

---

## 📚 Documentación de la API

Una vez que el servidor esté en marcha, puedes acceder a la documentación interactiva (generada por Swagger UI) en la siguiente URL para probar los endpoints directamente desde tu navegador:

🔗 **http://localhost:8000/docs**

### Endpoints Disponibles

| Método | Endpoint | Descripción | Cuerpo de la Petición (form-data) |
| :--- | :--- | :--- | :--- |
| `POST` | `/support` | Envía una pregunta por texto y una imagen opcional. | `text_query` (string), `image` (file) |
| `POST` | `/support/audio` | Envía una pregunta por audio y una imagen opcional. | `audio` (file), `image` (file) |
| `GET`  | `/` | Endpoint de bienvenida ||

### Ejemplo de Uso con `curl`

```bash
curl -X POST "http://localhost:8000/support/audio" \
-F "audio=@/ruta/a/tu/pregunta.mp3" \
-F "image=@/ruta/a/tu/captura.png"
