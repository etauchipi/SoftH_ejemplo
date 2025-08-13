import os
import uuid
from PIL import Image
from gtts import gTTS
import whisper
import base64
from io import BytesIO
from .app_code.params import (
    EMBEDDINGS_MODEL_NAME,
    LLM_MODEL_NAME,
    VISION_MODEL_NAME,
    KNOWLEDGE_BASE_DIR,
    DB_DIR,
    AUDIO_RESPONSES_DIR
)

# Importamos el conector de Ollama desde langchain-community
from langchain_community.chat_models import ChatOllama
from langchain_core.messages import HumanMessage
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import SentenceTransformerEmbeddings

# --- Constantes y directorios ---
DB_DIR = DB_DIR
AUDIO_RESPONSES_DIR = AUDIO_RESPONSES_DIR

# --- Inicialización de Modelos ---
print("Cargando modelos de soporte (Whisper, Embeddings)...")
whisper_model = whisper.load_model("base")
embedding_function = SentenceTransformerEmbeddings(model_name=EMBEDDINGS_MODEL_NAME)
vector_store = Chroma(persist_directory=DB_DIR, embedding_function=embedding_function)
retriever = vector_store.as_retriever(search_kwargs={"k": 5})

# --- INICIALIZACIÓN DE MODELOS OLLAMA ---
# Modelo principal para generar respuestas de texto
llm_text = ChatOllama(model=LLM_MODEL_NAME, temperature=0.5)

# Modelo de visión para describir las imágenes
llm_vision = ChatOllama(model=VISION_MODEL_NAME, temperature=0)

print("✅ Modelos cargados y listos.")


# --- Funciones de Servicio ---

def transcribe_audio(audio_path: str) -> str:
    """Transcribe un archivo de audio a texto."""
    print("---------------------------------------------")
    print(audio_path)
    result = whisper_model.transcribe(audio_path, fp16=False)
    return result['text']

def describe_image_with_llava(image_path: str) -> str:
    """
    Usa LLaVA para describir el contenido de una imagen.
    La imagen se convierte a base64 para enviarla en el prompt.
    """
    
    print(f"Describiendo imagen con LLaVA: {image_path}")
    
    try:
        # Abrir la imagen y convertirla a base64
        with Image.open(image_path) as img:
            print(f"Abre imagen --------->: {image_path}")
            buffer = BytesIO()
            img.save(buffer, format="JPEG")
            img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        # Crear el mensaje para LLaVA
        print(f"llm _ Abre imagen --------->: {image_path}")
        msg = llm_vision.invoke(
            [
                HumanMessage(
                    content=[
                        {"type": "text", "text": "Describe de forma concisa y técnica el contenido de esta captura de pantalla, extrayendo cualquier texto de error visible."},
                        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{img_base64}"},
                    ]
                )
            ]
        )
        print(f"Descripción de LLaVA: {msg.content}")
        return msg.content
    except Exception as e:
        print(f"❌ Error al describir la imagen con LLaVA: {e}")
        return ""


def generate_intelligent_answer(query: str, image_path: str = None) -> str:
    """
    Genera una respuesta usando LLaVA para la imagen y Llama3 para el texto + RAG.
    """
    image_context = ""
    if image_path:
        # Usamos nuestra nueva función para obtener la descripción de la imagen
        image_context = describe_image_with_llava(image_path)

    # 1. Obtener contexto relevante de la base de conocimiento (RAG)
    rag_context = ""
    if query:
        relevant_docs = retriever.get_relevant_documents(query)
        rag_context = "\n\n".join([doc.page_content for doc in relevant_docs])

    # 2. Construir el prompt final para Llama 3
    prompt = f"""
    Eres un asistente de soporte técnico experto para Etau Inc.
    
    Usa el siguiente CONTEXTO DE LA BASE DE CONOCIMIENTO:
    ---
    {rag_context}
    ---
    
    El usuario tiene la siguiente PREGUNTA: "{query}"
    
    Adicionalmente, el usuario envió una imagen que ha sido descrita como: "{image_context}"
    
    Basándote en toda esta información, proporciona una respuesta clara y directa para resolver el problema del usuario.
    Si el contexto no es suficiente, indícalo amablemente.
    """

    print("="*50)
    print("🚀 ENVIANDO PROMPT FINAL A PHI3:")
    print(prompt)
    print("="*50)
    
    # 3. Invocar a Llama 3 para la respuesta final
    response = llm_text.invoke(prompt)
    return response.content


def convert_text_to_speech(text: str, base_url: str) -> str:
    """Convierte texto a un archivo de audio .mp3 y devuelve su URL completa."""

    try:
        if not text or not text.strip():
            print("ADVERTENCIA: Se intentó generar audio de un texto vacío.")
            return "No se generó audio porque la respuesta de texto estaba vacía."
        tts = gTTS(text, lang='es', tld='com.mx')
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_RESPONSES_DIR, filename)
        tts.save(filepath)
        print(f"Audio generado exitosamente en: {filepath}")
        return f"{base_url}{AUDIO_RESPONSES_DIR}/{filename}"
    except Exception as e:
        print(f"❌ ERROR AL CREAR AUDIO CON GTTS: {e}")
        return "Error al generar el archivo de audio."