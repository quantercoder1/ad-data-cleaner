import streamlit as st
import pandas as pd
import hashlib
import requests

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="AdData Cleaner PRO", page_icon="💎", layout="centered")

# --- CONFIGURACIÓN DE CLAVES ---
# Tu clave maestra para entrar siempre sin validar en Lemon Squeezy
MASTER_KEY = "ADMIN-2026" 

def validar_con_lemon_squeezy(license_key):
    """
    Valida la clave contra la API oficial de Lemon Squeezy.
    Retorna: (Es_Valida, Mensaje_o_Nombre)
    """
    # Si usas tu clave maestra, pase directo
    if license_key == MASTER_KEY:
        return True, "Administrador (Master Key)"

    url = "https://api.lemonsqueezy.com/v1/licenses/activate"
    
    # Datos para la API
    payload = {
        "license_key": license_key,
        "instance_name": "AdDataCleaner_Web_User"
    }
    
    try:
        response = requests.post(url, data=payload)
        data = response.json()
        
        # Verificar si la respuesta fue exitosa
        if data.get("activated") is True:
            # Clave válida y activa
            meta = data.get("meta", {})
            return True, f"Licencia Activa ({license_key})"
        else:
            # Clave inválida, expirada o ya usada al máximo
            error_msg = data.get("error", "Clave no válida")
            return False, error_msg

    except Exception as e:
        return False, f"Error de conexión: {str(e)}"

# --- TEXTOS TRILINGÜES ---
textos = {
    "Español": {
        "titulo": "💎 AdData Cleaner PRO",
        "subtitulo": "Herramienta Enterprise: Limpieza y Hashing (Email, Teléfono, User ID).",
        "aviso": "Procesamiento seguro en memoria.",
        "subir": "Sube tu archivo (CSV o Excel)",
        "config": "Mapeo de Columnas",
        "col_email": "Columna de Email (Opcional)",
        "col_tel": "Columna de Teléfono (Opcional)",
        "col_id": "Columna de User ID (Opcional - CRM/Database ID)",
        "opciones": "Seguridad",
        "encriptar": "🛡️ Aplicar Hashing SHA256",
        "boton": "⚡ Procesar Datos",
        "bloqueo_titulo": "🔒 Activación de Producto",
        "bloqueo_msg": "Ingresa tu Licencia Oficial (Lemon Squeezy) para descargar.",
        "exito_auth": "✅ Licencia Verificada: ",
        "descargar": "📥 Descargar Archivo Seguro (.csv)",
        "error_clave": "🚫 Error de validación: "
    },
    "English": {
        "titulo": "💎 AdData Cleaner PRO",
        "subtitulo": "Enterprise Tool: Cleaning & Hashing (Email, Phone, User ID).",
        "aviso": "Secure in-memory processing.",
        "subir": "Upload File (CSV or Excel)",
        "config": "Column Mapping",
        "col_email": "Email Column (Optional)",
        "col_tel": "Phone Column (Optional)",
        "col_id": "User ID Column (Optional - CRM/Database ID)",
        "opciones": "Security",
        "encriptar": "🛡️ Apply SHA256 Hashing",
        "boton": "⚡ Process Data",
        "bloqueo_titulo": "🔒 Product Activation",
        "bloqueo_msg": "Enter your Official License Key (Lemon Squeezy) to download.",
        "exito_auth": "✅ License Verified: ",
        "descargar": "📥 Download Secure File (.csv)",
        "error_clave": "🚫 Validation Error: "
    },
    "Português": {
        "titulo": "💎 AdData Cleaner PRO",
        "subtitulo": "Ferramenta Enterprise: Limpeza e Hashing (Email, Telefone, User ID).",
        "aviso": "Processamento seguro na memória.",
        "subir": "Carregue seu arquivo (CSV ou Excel)",
        "config": "Mapeamento de Colunas",
        "col_email": "Coluna de Email (Opcional)",
        "col_tel": "Coluna de Telefone (Opcional)",
        "col_id": "Coluna de User ID (Opcional - CRM/Database ID)",
        "opciones": "Segurança",
        "encriptar": "🛡️ Aplicar Hashing SHA256 (LGPD)",
        "boton": "⚡ Processar Dados",
        "bloqueo_titulo": "🔒 Ativação do Produto",
        "bloqueo_msg": "Insira sua Licença Oficial (Lemon Squeezy) para baixar.",
        "exito_auth": "✅ Licença Verificada: ",
        "descargar": "📥 Baixar Arquivo Seguro (.csv)",
        "error_clave": "🚫 Erro de validação: "
    }
}

# --- FUNCIONES DE LIMPIEZA ---
def clean_generic(val):
    """Limpia espacios y nulos basicos"""
    s = str(val).strip()
    return "" if s.lower() in ['nan', 'none', '', 'null'] else s

def clean_phone_logic(val):
    """Solo digitos"""
    s = clean_generic(val)
    if not s: return ""
    return "".join(filter(str.isdigit, s))

def apply_hash(val):
    """Aplica SHA256 si hay valor"""
    if not val: return ""
    return hashlib.sha256(val.lower().encode()).hexdigest()

# --- INTERFAZ ---
idioma = st.sidebar.selectbox("Language / Idioma / Idioma", ["English", "Español", "Português"])
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
        cols = ["-- Ignorar --"] + df.columns.tolist()
        
        c1, c2, c3 = st.columns(3)
        with c1: email_col = st.selectbox(t["col_email"], cols)
        with c2: phone_col = st.selectbox(t["col_tel"], cols)
        with c3: id_col = st.selectbox(t["col_id"], cols)
        
        st.divider()
        
        # --- AQUÍ ESTABA EL ERROR, YA ESTÁ CORREGIDO ---
        hashing = st.checkbox(t["encriptar"], value=True)

        if st.button(t["boton"]):
            clean_df = df.copy()

            with st.spinner("Processing..."):
                # 1. EMAIL
                if email_col != "-- Ignorar --":
                    clean_df[email_col] = clean_df[email_col].apply(clean_generic).str.lower()
                    if hashing:
                        clean_df[email_col] = clean_df[email_col].apply(apply_hash)

                # 2. TELÉFONO
                if phone_col != "-- Ignorar --":
                    clean_df[phone_col] = clean_df[phone_col].apply(clean_phone_logic)
                    if hashing:
                        clean_df[phone_col] = clean_df[phone_col].apply(apply_hash)
                
                # 3. USER ID
                if id_col != "-- Ignorar --":
                    # Solo quitamos espacios, no borramos simbolos raros de IDs
                    clean_df[id_col] = clean_df[id_col].apply(clean_generic)
                    if hashing:
                        clean_df[id_col] = clean_df[id_col].apply(apply_hash)

                st.session_state['data_final'] = clean_df.to_csv(index=False).encode('utf-8')
                st.session_state['ready'] = True

    except Exception as e:
        st.error(f"Error: {e}")

# --- COBRO / ACTIVACIÓN ---
if st.session_state.get('ready'):
    st.divider()
    st.subheader(t["bloqueo_titulo"])
    st.write(t["bloqueo_msg"])
    
    key_input = st.text_input("License Key:", type="password")
    
    # Validamos si se presionó el botón o si ya hay una clave ingresada y se dio Enter
    if st.button("Validar / Validate / Validar"):
        if key_input:
            es_valida, mensaje = validar_con_lemon_squeezy(key_input)
            
            if es_valida:
                st.success(f"{t['exito_auth']} {mensaje}")
                st.download_button(
                    label=t["descargar"],
                    data=st.session_state['data_final'],
                    file_name="secure_data_processed.csv",
                    mime="text/csv"
                )
            else:
                st.error(f"{t['error_clave']} {mensaje}")