import streamlit as st
import requests
import tempfile
from fpdf import FPDF
from docx import Document

st.set_page_config(page_title="Chat AV IA", layout="centered")

# --- ESTILOS modo oscuro y botones personalizados ---
st.markdown("""
    <style>
    body, .stApp { background-color: #252429; color: #f6f6f6;}
    .bienvenida { text-align: center; font-size: 1.2em; margin-bottom: 1.5em; color: #f6f6f6; }
    .stTextInput > div > input, .stTextArea textarea {
        background: #282c34; color: #f6f6f6;
    }
    .stButton>button { background-color: #ee5544; color: white; border-radius: 8px;}
    .stButton>button:hover:enabled { background-color: #fff; color: #ee5544; border: 2px solid #ee5544;}
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='bienvenida'>Hola, soy tu asistente AV.<br>¿En qué te puedo ayudar hoy?</div>", unsafe_allow_html=True)

pregunta = st.text_area("Pregunta o consulta:")

archivo = st.file_uploader(
    "Adjuntá un archivo (PDF, DOCX, TXT, PNG, JPG, JPEG) para analizar (opcional):",
    type=["pdf", "docx", "txt", "png", "jpg", "jpeg"]
)

def limpiar_a_latin1(texto):
    return texto.encode('latin1', 'replace').decode('latin1')

if st.button("Enviar consulta"):
    if not pregunta and not archivo:
        st.warning("Por favor, escribí una consulta o subí un archivo.")
        st.stop()

    with st.spinner("Procesando consulta con IA..."):
        respuesta_final = ""
        placeholder = st.empty()
        try:
            files = {"archivo": archivo} if archivo else None
            data = {"pregunta": pregunta}
            with requests.post("https://bc3d-200-123-154-215.ngrok-free.app/consulta", data=data, files=files, stream=True, timeout=300) as response:
                respuesta_parcial = ""
                # Streaming: vamos sumando los trozos y refrescando en pantalla
                for chunk in response.iter_content(chunk_size=256):
                    if chunk:
                        text_chunk = chunk.decode("utf-8", errors="replace")
                        respuesta_parcial += text_chunk
                        # Mostramos progresivamente en la app
                        placeholder.markdown(f"<div style='padding:1em 0;font-size:1.1em;'>{respuesta_parcial}</div>", unsafe_allow_html=True)
                respuesta_final = respuesta_parcial

            # Muestra la respuesta final por si hubo algún remanente
            placeholder.markdown(f"<div style='padding:1em 0;font-size:1.1em;'>{respuesta_final}</div>", unsafe_allow_html=True)

            # PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for linea in respuesta_final.split("\n"):
                pdf.multi_cell(0, 10, limpiar_a_latin1(linea))
            pdf_bytes = pdf.output(dest='S').encode('latin1')
            st.download_button("⬇️ Descargar en PDF", pdf_bytes, file_name="respuesta.pdf", mime="application/pdf")

            # DOCX
            doc = Document()
            for linea in respuesta_final.split("\n"):
                doc.add_paragraph(limpiar_a_latin1(linea))
            with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as tmp:
                doc.save(tmp.name)
                tmp.seek(0)
                docx_bytes = tmp.read()
            st.download_button("⬇️ Descargar en DOCX", docx_bytes, file_name="respuesta.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

        except Exception as e:
            placeholder.error(f"Ocurrió un error: {e}")



