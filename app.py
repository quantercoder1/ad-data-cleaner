import streamlit as st
import pandas as pd
import hashlib
import io

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AdData Cleaner & Hasher", page_icon="🎯", layout="centered")

# --- LÓGICA DE IDIOMA ---
idioma = st.sidebar.selectbox("Language / Idioma", ["Español", "English"])

textos = {
    "Español": {
        "titulo": "🎯 AdData Cleaner & Hasher",
        "subtitulo": "Limpia y encripta tus listas de clientes para Facebook/Google Ads en segundos.",
        "subir": "Sube tu archivo (CSV o Excel)",
        "config": "Configuración de Columnas",
        "col_email": "Selecciona la columna de Email",
        "col_tel": "Selecciona la columna de Teléfono (Opcional)",
        "opciones": "Opciones de Procesamiento",
        "encriptar": "🛡️ Encriptar datos (SHA256) - Requerido para privacidad (GDPR/CCPA)",
        "boton": "🚀 Procesar y Limpiar",
        "exito": "¡Archivo procesado con éxito!",
        "descargar": "Descargar Archivo Limpio",
        "error_archivo": "Por favor sube un archivo válido.",
        "aviso": "Tus datos se procesan en memoria y no se guardan en ningún servidor."
    },
    "English": {
        "titulo": "🎯 AdData Cleaner & Hasher",
        "subtitulo": "Clean and hash your customer lists for Facebook/Google Ads in seconds.",
        "subir": "Upload your file (CSV or Excel)",
        "config": "Column Mapping",
        "col_email": "Select Email Column",
        "col_tel": "Select Phone Column (Optional)",
        "opciones": "Processing Options",
        "encriptar": "🛡️ Hash Data (SHA256) - Required for privacy (GDPR/CCPA)",
        "boton": "🚀 Process & Clean",
        "exito": "File processed successfully!",
        "descargar": "Download Clean File",
        "error_archivo": "Please upload a valid file.",
        "aviso": "Your data is processed in-memory and is never stored on any server."
    }
}

t = textos[idioma]

# --- INTERFAZ PRINCIPAL ---
st.title(t["titulo"])
st.write(t["subtitulo"])
st.info(t["aviso"])

uploaded_file = st.file_uploader(t["subir"], type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
            
        st.write("Vista previa / Preview:", df.head(3))

        st.subheader(t["config"])
        columns = df.columns.tolist()
        
        email_col = st.selectbox(t["col_email"], columns)
        phone_col = st.selectbox(t["col_tel"], ["None"] + columns)

        st.subheader(t["opciones"])
        usar_hashing = st.checkbox(t["encriptar"], value=True)

        if st.button(t["boton"]):
            with st.spinner("Processing..."):
                clean_df = pd.DataFrame()
                clean_df['email'] = df[email_col].astype(str).str.strip().str.lower()
                if phone_col != "None":
                    clean_df['phone'] = df[phone_col].astype(str).str.replace(r'\D', '', regex=True)
                
                if usar_hashing:
                    clean_df['email'] = clean_df['email'].apply(lambda x: hashlib.sha256(x.encode()).hexdigest())
                    if phone_col != "None":
                        clean_df['phone'] = clean_df['phone'].apply(lambda x: hashlib.sha256(x.encode()).hexdigest())

                csv_buffer = clean_df.to_csv(index=False).encode('utf-8')
                
                st.success(t["exito"])
                st.download_button(
                    label=t["descargar"],
                    data=csv_buffer,
                    file_name="ad_data_clean_hashed.csv",
                    mime="text/csv"
                )
    except Exception as e:
        st.error(f"Error: {e}")