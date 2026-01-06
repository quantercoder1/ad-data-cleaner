import streamlit as st
import pandas as pd
import hashlib

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AdData Cleaner PRO", page_icon="💎", layout="centered")

# --- BASE DE DATOS DE CLIENTES (SIMULADA) ---
# En el futuro, esto se conectará a la API de Lemon Squeezy.
# Por ahora, tú agregas manualmentes las claves aquí cuando te paguen.
LICENCIAS_ACTIVAS = {
    "DEMO-USER": {"nombre": "Usuario Beta", "valida": True},
    "CLIENTE-001": {"nombre": "Agencia Alpha", "valida": True},
    "SUPER-ADMIN": {"nombre": "Admin", "valida": True}
}

def validar_licencia(clave):
    """Verifica si la clave existe en nuestra 'base de datos'"""
    if clave in LICENCIAS_ACTIVAS:
        if LICENCIAS_ACTIVAS[clave]["valida"]:
            return True, LICENCIAS_ACTIVAS[clave]["nombre"]
    return False, None

# --- TEXTOS ---
textos = {
    "Español": {
        "titulo": "💎 AdData Cleaner PRO",
        "subtitulo": "Herramienta premium: Limpia formatos y encripta (SHA256) sin perder columnas.",
        "aviso": "Tus datos se procesan localmente. Se mantienen todas las columnas originales.",
        "subir": "Sube tu archivo (CSV o Excel)",
        "config": "Selecciona las columnas a limpiar",
        "col_email": "¿Cuál es tu columna de Email?",
        "col_tel": "¿Cuál es tu columna de Teléfono? (Opcional)",
        "opciones": "Seguridad",
        "encriptar": "🛡️ Aplicar Hashing SHA256 (GDPR)",
        "boton": "⚡ Procesar Archivo",
        "bloqueo_titulo": "🔒 Validación de Licencia",
        "bloqueo_msg": "Ingresa tu clave de licencia única para descargar el resultado.",
        "exito_auth": "✅ Licencia Verificada. Hola, ",
        "descargar": "📥 Descargar Data Lista (.csv)",
        "error_clave": "🚫 Clave inválida o expirada. Contacta a soporte."
    },
    "English": {
        "titulo": "💎 AdData Cleaner PRO",
        "subtitulo": "Premium tool: Clean formats and hash (SHA256) keeping all original columns.",
        "aviso": "Data processed locally. All original columns are preserved.",
        "subir": "Upload your file (CSV or Excel)",
        "config": "Select columns to clean",
        "col_email": "Which is your Email column?",
        "col_tel": "Which is your Phone column? (Optional)",
        "opciones": "Security",
        "encriptar": "🛡️ Apply SHA256 Hashing (GDPR)",
        "boton": "⚡ Process File",
        "bloqueo_titulo": "🔒 License Validation",
        "bloqueo_msg": "Enter your unique license key to download the result.",
        "exito_auth": "✅ License Verified. Hello, ",
        "descargar": "📥 Download Ready Data (.csv)",
        "error_clave": "🚫 Invalid or expired key. Contact support."
    }
}

# --- INTERFAZ ---
idioma = st.sidebar.selectbox("Language / Idioma", ["Español", "English"])
t = textos[idioma]

st.title(t["titulo"])
st.markdown(t["subtitulo"])
st.info(t["aviso"])

uploaded_file = st.file_uploader(t["subir"], type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        # Cargar datos
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.write("Preview:", df.head(3))

        # Configuración
        st.subheader(t["config"])
        cols = df.columns.tolist()
        
        # Selectores
        email_col = st.selectbox(t["col_email"], cols)
        phone_col = st.selectbox(t["col_tel"], ["-- Ignorar / Ignore --"] + cols)
        
        st.divider()
        usar_hashing = st.checkbox(t["encriptar"], value=True)

        if st.button(t["boton"]):
            # TRUCO: Trabajamos sobre una copia para no borrar las otras columnas
            clean_df = df.copy()

            with st.spinner("Processing..."):
                # 1. Limpieza de Email (Sobreescribe la columna original limpia)
                clean_df[email_col] = clean_df[email_col].astype(str).str.strip().str.lower()
                
                # 2. Hashing Email
                if usar_hashing:
                    clean_df[email_col] = clean_df[email_col].apply(lambda x: hashlib.sha256(x.encode()).hexdigest())

                # 3. Limpieza de Teléfono (Si se seleccionó)
                if phone_col != "-- Ignorar / Ignore --":
                    # Quitar todo lo que no sea número
                    clean_df[phone_col] = clean_df[phone_col].astype(str).str.replace(r'\D', '', regex=True)
                    # Hashing Teléfono
                    if usar_hashing:
                        clean_df[phone_col] = clean_df[phone_col].apply(lambda x: hashlib.sha256(x.encode()).hexdigest())

                # Guardar en sesión
                st.session_state['data_final'] = clean_df.to_csv(index=False).encode('utf-8')
                st.session_state['ready'] = True

    except Exception as e:
        st.error(f"Error: {e}")

# --- SISTEMA DE LICENCIAS ---
if st.session_state.get('ready'):
    st.divider()
    st.subheader(t["bloqueo_titulo"])
    st.write(t["bloqueo_msg"])
    
    licencia_input = st.text_input("License Key / Clave:", type="password")
    
    if licencia_input:
        valida, nombre_cliente = validar_licencia(licencia_input)
        
        if valida:
            st.success(f"{t['exito_auth']} {nombre_cliente}!")
            st.download_button(
                label=t["descargar"],
                data=st.session_state['data_final'],
                file_name="clean_data_full.csv",
                mime="text/csv"
            )
        else:
            st.error(t["error_clave"])