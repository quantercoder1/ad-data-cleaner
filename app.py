import streamlit as st
import pandas as pd
import hashlib

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="AdData Cleaner PRO", page_icon="💎", layout="centered")

# --- BASE DE DATOS DE CLIENTES ---
# Agrega aquí las claves de tus futuros clientes
LICENCIAS_ACTIVAS = {
    "DEMO-USER": {"nombre": "Usuario Beta", "valida": True},
    "CLIENTE-001": {"nombre": "Agencia Alpha", "valida": True},
    "ADMIN": {"nombre": "Admin", "valida": True}
}

def validar_licencia(clave):
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

# --- FUNCIÓN DE LIMPIEZA SEGURA ---
def clean_and_hash(val, hash_enabled):
    """Limpia el valor y aplica hash solo si no está vacío"""
    # 1. Convertir a string y quitar espacios
    val_str = str(val).strip().lower()
    
    # 2. Si es 'nan', vacio o 'none', devolver vacío sin hashear
    if val_str in ['nan', 'none', '', 'null']:
        return ""
    
    # 3. Aplicar Hash si está activado
    if hash_enabled:
        return hashlib.sha256(val_str.encode()).hexdigest()
    
    return val_str

def clean_phone(val, hash_enabled):
    """Específico para teléfonos: quita letras antes de hashear"""
    val_str = str(val).strip()
    if val_str in ['nan', 'none', '', 'null']:
        return ""
    
    # Quitar todo lo que no sea dígito
    nums_only = "".join(filter(str.isdigit, val_str))
    
    if not nums_only: # Si quedó vacío
        return ""

    if hash_enabled:
        return hashlib.sha256(nums_only.encode()).hexdigest()
    
    return nums_only

# --- INTERFAZ ---
idioma = st.sidebar.selectbox("Language / Idioma", ["Español", "English"])
t = textos[idioma]

st.title(t["titulo"])
st.markdown(t["subtitulo"])
st.info(t["aviso"])

uploaded_file = st.file_uploader(t["subir"], type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.write("Preview:", df.head(3))

        st.subheader(t["config"])
        cols = df.columns.tolist()
        
        email_col = st.selectbox(t["col_email"], cols)
        phone_col = st.selectbox(t["col_tel"], ["-- Ignorar / Ignore --"] + cols)
        
        st.divider()
        usar_hashing = st.checkbox(t["encriptar"], value=True)

        if st.button(t["boton"]):
            clean_df = df.copy() # Copia segura

            with st.spinner("Processing..."):
                # Aplicar limpieza inteligente fila por fila
                clean_df[email_col] = clean_df[email_col].apply(lambda x: clean_and_hash(x, usar_hashing))

                if phone_col != "-- Ignorar / Ignore --":
                    clean_df[phone_col] = clean_df[phone_col].apply(lambda x: clean_phone(x, usar_hashing))

                # Guardar resultado
                st.session_state['data_final'] = clean_df.to_csv(index=False).encode('utf-8')
                st.session_state['ready'] = True

    except Exception as e:
        st.error(f"Error: {e}")

# --- LICENCIAS ---
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
                file_name="clean_data_secure.csv",
                mime="text/csv"
            )
        else:
            st.error(t["error_clave"])