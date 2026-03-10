#C:\AMUGITHUB\chat_asistente_automatico\chat_asistente_automatico.py
import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import google.generativeai as genai
from pinecone import Pinecone
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = FastAPI(title="Microservicio IA Gemini + Pinecone")

# 1. Configurar API de Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
# Usamos el modelo más rápido y eficiente
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Configurar Pinecone (Base de Datos Vectorial)
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
# Descomenta y pon el nombre de tu índice cuando lo crees en Pinecone
# index = pc.Index("mi-indice-productos") 

# 3. Base de Datos en JSON (Aquí puedes cambiar a Firestore/SQL luego)
base_datos_local = {
    "zapatillas_rojas": {"precio": 120, "stock": 5},
    "camiseta_azul": {"precio": 25, "stock": 0}
}

# Modelos para recibir datos de Typebot
class TypebotRequest(BaseModel):
    phone: str
    message: str

class TypebotResponse(BaseModel):
    respuesta_ia: str
    handoff_humano: bool

@app.post("/api/chat", response_model=TypebotResponse)
async def recibir_mensaje(req: TypebotRequest):
    try:
        mensaje_usuario = req.message
        
        # --- LÓGICA RAG (Retrieval-Augmented Generation) ---
        # A. (Opcional) Buscar en Pinecone contexto relevante
        # vector_search = index.query(vector=[...], top_k=3, include_metadata=True)
        # contexto_pinecone = vector_search['matches']
        contexto_pinecone = "Contexto simulado: Nuestra tienda cierra a las 6pm."

        # B. Buscar en nuestra BD local (JSON)
        contexto_db = str(base_datos_local)

        # C. Armar el Prompt para Gemini
        prompt_final = f"""
        Eres un asistente de ventas de WhatsApp. Sé breve y amable.
        Contexto de la empresa: {contexto_pinecone}
        Inventario actual: {contexto_db}
        
        Usuario pregunta: {mensaje_usuario}
        """

        # D. Generar respuesta con Gemini
        respuesta = model.generate_content(prompt_final)
        texto_generado = respuesta.text

        # Lógica de Handoff (si Gemini no sabe o el usuario se enoja)
        necesita_humano = "humano" in mensaje_usuario.lower() or "asesor" in mensaje_usuario.lower()

        return TypebotResponse(
            respuesta_ia=texto_generado,
            handoff_humano=necesita_humano
        )

    except Exception as e:
        print(f"Error: {e}")
        return TypebotResponse(respuesta_ia="Dame un momento, estamos experimentando fallas técnicas.", handoff_humano=True)