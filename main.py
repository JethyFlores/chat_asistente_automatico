import os
import json
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Literal, Dict, List
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Configuración Inicial
load_dotenv()
app = FastAPI(title="Microservicio IA - AAAMundial")

# Configuramos Gemini (Usamos 1.5-flash por su velocidad brutal para chat)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')

# 2. Bases de Datos Inmutables (Igual que en tu Typebot)
CATALOGO_MODULOS = {
    "MOD_UAFE": {
        "detalle": "⚠️ *Ojo: cualquier error en el Acta o Declaración puede generar rechazo en la Supercias y multas de $5.000 a $9.200* ⚠️\nEsta herramienta le entrega el kit legal completo para evitar riesgos.\n\n✅ *Funcionalidades:*\n1) Generación automática Manual PLA/ FT\n2) Generación automática Matriz de Riesgo\n3) Plantillas debida diligencia\n4) Plantillas informes para Superintendencia de Compañías\n5) Generación de documentos para la calificación del oficial de cumplimiento\n6) Curso grabado de cómo calificarse cómo oficial de cumplimiento y obligaciones ante UAFE y Supercias",
        "video": "https://storage.googleapis.com/amuoctubre_cloudbuild/Videos%20atencion%20al%20cliente/UAFE%20%C3%9ALTIMO.mp4"
    },
    "MOD_SRI": {
        "detalle": "✅ *Funcionalidades SRI:*\n1) Descarga masiva Automática (XML y PDF) de hasta 5 años atrás.\n2) Reportes automáticos en Excel para sus declaraciones.\n3) Generación de ATS automático sin digitar nada.",
        "video": "https://storage.googleapis.com/amuoctubre_cloudbuild/Videos%20atencion%20al%20cliente/ENVIAR%20PRODUCTOS%20DESCARGA%20.mp4"
    },
    "MOD_SOCIETARIO": {
        "detalle": "✅ *Funcionalidades SUPERCIAS:*\n1) Mapeo automático del Formulario 101.\n2) Generación de los 4 Estados Financieros (TXT y Excel).\n3) Notas Explicativas automáticas.",
        "video": "https://storage.googleapis.com/amuoctubre_cloudbuild/Videos%20atencion%20al%20cliente/EEFF.mp4"
    },
    "MOD_REBEFICS": {
        "detalle": "✅ *Funcionalidades REBEFICS:*\n1) Generación automática en Excel y XML (Sin errores).\n2) Carga histórica de años anteriores.\n3) Validación inteligente ante el SRI.",
        "video": "https://storage.googleapis.com/amuoctubre_cloudbuild/Videos%20atencion%20al%20cliente/Rebefics.mp4"
    }
}

DB_LINKS = {
    "MOD_SOCIETARIO": "https://buy.stripe.com/6oUdR96g74Rt21WeFI0kE1x",
    "MOD_SRI": "https://buy.stripe.com/9B64gz9sjdnZ7mg8hk0kE1w",
    "MOD_DATOS": "https://buy.stripe.com/cNifZh5c32Jl5e80OS0kE1r",
    "MOD_UAFE": "https://buy.stripe.com/bJe9ATfQHdnZdKEaps0kE1D",
    "MOD_RDEP": "https://buy.stripe.com/28E3cveMD83F21Wbtw0kE1F",
    "MOD_REBEFICS": "https://buy.stripe.com/fZu7sLeMD97JbCwdBE0kE1E",
    "MOD_LABORAL": "https://buy.stripe.com/fZucN50VN3Np5e8btw0kE1y",
    "PACK_FULL": "https://buy.stripe.com/7sY9AT1ZR83F8qkeFI0kE1s",
    "NINGUNO": "https://buy.stripe.com/7sY9AT1ZR83F8qkeFI0kE1s"
}

CUENTAS_BANCARIAS = """
🏦 *TRANSFERENCIA O DEPÓSITO*

*Banco Produbanco*
Cuenta de Ahorros: 12040459190
Beneficiario: Assurance Advisory Accounting Cia Ltda
RUC: 1792970148001

*Banco Pichincha:* Ahorros 2204446191
*Banco Guayaquil:* Ahorros 36370284
*Banco Pacífico:* Ahorros 1053793641
Beneficiario: Henry Flores
Cédula: 1718249749

Por favor, ayúdame con la foto del comprobante por este medio para proceder con la activación. 🚀"""

DETALLE_PACK = """
*Funciones disponibles en el Ecosistema:*
• Validador retenciones 2026
• Clasificador automático de gastos
• Rebefics
• Descarga masiva, Reportes y ATS
• Rdep
• Balances Super Cías
• Formulario Utilidades MDT
• Anexo Dividendos y Declaración Patrimonial
• Chatbot tributario y societario
• Informe Cumplimiento Tributario
• Facturación Electrónica Masiva
• Riesgo fiscal
• Manuales, matrices y debida diligencia UAFE
• Décimos Tercer y Cuarto Sueldo MDT
• Planes laborales y protocolos de acoso
• Cumplimiento Protección Datos Personales

*Planes disponibles:*
🚀 *Plan Empresarial ($999/año)* todas las funciones + Desarrollo extra
🏢 *Plan Completo ($499/año)* todas las funciones + Nuevas en el año
💻 *Plan Esencial ($199/año)* por 1 función a su elección
⏱️ *Plan Temporal ($99/30 días)* por 1 función para 1 solo ruc por 30 días"""

UPSELL_TEXT = "\n\n💰 *Inversión individual:* $199/año.\nPero siendo 100% transparente contigo: por **$499** te llevas este módulo Y las otras 16 herramientas del Pack Full (Laboral, Societario, UAFE, etc). Es matemáticamente mejor negocio.\n\n¿Te paso el detalle de todo lo que incluye el Pack Full para que compares o prefieres ir solo con esta función?"

# 3. Modelos de Entrada/Salida (Pydantic)
class TypebotRequest(BaseModel):
    phone: str
    message: str

class TypebotResponse(BaseModel):
    respuesta_ia: str
    url_video: str | None = None
    vid_pack_1: str | None = None
    vid_pack_2: str | None = None
    vid_pack_3: str | None = None
    vid_pack_4: str | None = None

# 4. El "Molde" estricto para Gemini
class EstructuraIA(BaseModel):
    pensamiento_estrategico: str
    id_producto: Literal["MOD_DATOS", "MOD_SRI", "MOD_REBEFICS", "MOD_LABORAL", "MOD_SOCIETARIO", "MOD_UAFE", "MOD_RDEP", "MOD_ICT", "MOD_CHATBOT", "MOD_GASTOS", "MOD_DECIMOS", "PACK_FULL", "NINGUNO"]
    mensaje_whatsapp: str
    accion_mostrar_detalle_individual: bool
    accion_mostrar_video_individual: bool
    accion_mostrar_lista_pack: bool
    accion_mostrar_videos_pack_separados: bool
    accion_mostrar_pagos: bool

# Memoria Temporal (Diccionario en RAM)
memoria_chats: Dict[str, List[str]] = {}

@app.post("/api/chat", response_model=TypebotResponse)
async def chat_endpoint(req: TypebotRequest):
    # 1. Recuperar o iniciar historial
    if req.phone not in memoria_chats:
        memoria_chats[req.phone] = []
    
    historial = "\n".join(memoria_chats[req.phone][-10:]) # Últimos 10 mensajes

    # 2. El Prompt Maestro de Hormozi
    prompt_sistema = f"""
    SISTEMA: Eres Henry Flores, Director de AAAMundial. Eres un Vendedor Consultivo. Escribes en WhatsApp como un humano real: DIRECTO AL GRANO, mensajes EXTRA CORTOS (máximo 1 o 2 líneas), empático. NUNCA suenas como un robot ni mandas testamentos.
    
    REGLA DE ORO: LEE el 'Historial de Chat'. Si ya saludaste, no vuelvas a saludar. Si el usuario te habla informal, responde profesional pero relajado.
    
    ESTRATEGIA DE VENTA (Hormozi):
    1. INDAGACIÓN: Si no sabes qué busca, indaga su dolor normativo/contable (SRI, UAFE, Laboral).
    2. DETALLE DE PRODUCTO: Si te pregunta qué incluye una función específica, dale la razón y activa 'accion_mostrar_detalle_individual'.
    3. EL UPSELL: Activa 'accion_mostrar_lista_pack' si acepta ver el pack completo.
    4. CIERRE: Si muestra intención de pago ('quiero pagar', 'cuenta', 'comprar'), celebra y activa 'accion_mostrar_pagos'.
    
    Historial de la conversación:
    {historial}
    
    Mensaje actual del cliente: {req.message}
    """

    try:
        # 3. Llamamos a Gemini forzando a que devuelva nuestra estructura Pydantic
        respuesta_cruda = model.generate_content(
            prompt_sistema,
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                response_schema=EstructuraIA
            )
        )
        
        # Convertimos el JSON de Gemini a un diccionario de Python
        datos_ia = json.loads(respuesta_cruda.text)
        
        mensaje_final = datos_ia["mensaje_whatsapp"]
        id_prod = datos_ia["id_producto"]
        url_vid = None