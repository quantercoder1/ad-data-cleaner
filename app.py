import streamlit as st
import pandas as pd
import hashlib

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AdData Cleaner PRO", page_icon="💎", layout="centered")

# --- LÓGICA DE IDIOMA ---
idioma = st.sidebar.selectbox("Language / Idioma", ["Español", "English"])

textos = {
    "Español": {
        "titulo": "💎 AdData Cleaner PRO",
        "subtitulo": "Herramienta premium para limpiar y hashear audiencias de Meta/Google Ads.",
        "aviso": "Tus datos se procesan en memoria localmente. Privacidad 100% garantizada.",
        "subir": "Sube tu archivo sucio (CSV/Excel)",
        "config": "Mapeo de Datos",
        "col_email": "Columna de Email",
        "col_tel": "Columna de Teléfono (Opcional)",
        "opciones": "Seguridad & Formato",
        "encriptar": "Aplicar Hashing SHA256 (GDPR Compliance)",
        "boton": "⚡ Procesar Archivo",
        "bloqueo_titulo": "🔒 Desbloquear Descarga",
        "bloqueo_msg": "Esta herramienta es exclusiva. Ingresa tu Clave de Acceso para descargar.",
        "bloqueo_input": "Ingresa tu Clave de Licencia",
        "bloqueo_cta": "¿No tienes clave? Solicita una DEMO o Licencia aquí:",
        "exito_auth": "✅ Licencia Válida. Descarga habilitada.",
        "descargar": "📥 Descargar Clean Data (.csv)",
        "error_clave": "Clave incorrecta.",
        "link_texto": "Contactar al Desarrollador en LinkedIn"
    },
    "English": {
        "titulo": "💎 AdData Cleaner PRO",
        "subtitulo": "Premium tool to clean and hash Meta/Google Ads audiences.",
        "aviso": "Data is processed in-memory locally. 100% Privacy guaranteed.",
        "subir": "Upload dirty file (CSV/Excel)",
        "config": "Data Mapping",
        "col_email": "Email Column",
        "col_tel": "Phone Column (Optional)",
        "opciones": "Security & Formatting",
        "encriptar": "Apply SHA256 Hashing (GDPR Compliance)",
        "boton": "⚡ Process File",
        "bloqueo_titulo": "🔒 Unlock Download",
        "bloqueo_msg": "This is an exclusive tool. Enter your Access Key to download.",
        "bloqueo_input": "Enter License Key",
        "bloqueo_cta": "No key? Request a DEMO or License here:",
        "exito_auth": "✅ Key Valid. Download enabled.",
        "descargar": "📥 Download Clean Data (.csv)",
        "error_clave": "Invalid Key.",
        "link_texto": "Contact Developer on LinkedIn"
    }
}

t = textos[idioma]

# --- TU CLAVE MAESTRA (Cámbiala por lo que quieras) ---
CLAVE_MAESTRA = "BETA2025"  
# -----------------------------------------------------

# --- INTERFAZ ---
st.title(t["titulo"])
st.markdown(f"*{t['subtitulo']}*")
st.info(t["aviso"])

uploaded_file = st.file_uploader(t["subir"], type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.write("Preview:", df.head(3))

        col1, col2 = st.columns(2)
        with col1:
            email_col = st.selectbox(t["col_email"], df.columns)
        with col2:
            phone_col = st.selectbox(t["col_tel"], ["None"] + df.columns.tolist())

        usar_hashing = st.checkbox(t["encriptar"], value=True)

        if st.button(t["boton"]):
            # Procesamiento (Ocurre oculto)
            clean_df = pd.DataFrame()
            clean_df['email'] = df[email_col].astype(str).str.strip().str.lower()
            if phone_col != "None":
                clean_df['phone'] = df[phone_col].astype(str).str.replace(r'\D', '', regex=True)
            
            if usar_hashing:
                clean_df['email'] = clean_df['email'].apply(lambda x: hashlib.sha256(x.encode()).hexdigest())
                if phone_col != "None":
                    clean_df['phone'] = clean_df['phone'].apply(lambda x: hashlib.sha256(x.encode()).hexdigest())
            
            # Guardar en sesión para no perderlo al recargar
            st.session_state['data_procesada'] = clean_df.to_csv(index=False).encode('utf-8')
            st.session_state['archivo_listo'] = True

    except Exception as e:
        st.error(f"Error: {e}")

# --- SECCIÓN DE COBRO / BLOQUEO ---
if st.session_state.get('archivo_listo'):
    st.divider()
    st.subheader(t["bloqueo_titulo"])
    st.write(t["bloqueo_msg"])
    
    # Input de la clave
    user_key = st.text_input(t["bloqueo_input"], type="password")
    
    if user_key == CLAVE_MAESTRA:
        st.success(t["exito_auth"])
        st.download_button(
            label=t["descargar"],
            data=st.session_state['data_procesada'],
            file_name="clean_hashed_data.csv",
            mime="text/csv"
        )
    else:
        st.warning("⚠️")
        st.markdown(f"**{t['bloqueo_cta']}**")
        
        # --- ¡PON TU LINK DE LINKEDIN AQUÍ! ---
        LINK_LINKEDIN = "