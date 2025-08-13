import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import Chroma

KNOWLEDGE_BASE_DIR = './knowledge_base/'
DB_DIR = './db'

def load_documents_from_directory(directory: str):
    """Carga documentos .txt y .pdf de un directorio."""
    all_documents = []
    files_to_load = ["ManualDeUsusarioSofHelp.pdf", "Preguntas Frecuentes (FAQ).txt", "Errores Comunes en SoftHelp.txt"]

    for filename in files_to_load:
        filepath = os.path.join(directory, filename)
        
        print(f"documento: {filepath}")
        
        if not os.path.exists(filepath):
            print(f"Advertencia: El archivo {filepath} no fue encontrado.")
            continue
        try:
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(filepath)
            elif filename.endswith(".txt"):
                loader = TextLoader(filepath, encoding='utf-8')
            all_documents.extend(loader.load())
            print(f"Cargado exitosamente: {filename}")
        except Exception as e:
            print(f"Error cargando el archivo {filepath}: {e}")
    return all_documents

print("Iniciando la ingesta de la base de conocimiento...")
documents = load_documents_from_directory(KNOWLEDGE_BASE_DIR)

if documents:
    print("\nDividiendo documentos en trozos...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1200, chunk_overlap=150)
    texts = text_splitter.split_documents(documents)

    print("Creando embeddings con 'all-MiniLM-L6-v2'...")
    embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

    print(f"Guardando embeddings en el directorio '{DB_DIR}'...")
    vectordb = Chroma.from_documents(
        documents=texts,
        embedding=embeddings,
        persist_directory=DB_DIR
    )
    vectordb.persist()

    print("\n✅ ¡Proceso completado! La base de conocimiento ha sido procesada.")
    print(f"Total de trozos de texto para búsqueda: {len(texts)}")
else:
    print("\n❌ No se cargaron documentos. Abortando.")