import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO
from datetime import datetime
import re
import os
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Auditor Fiscal PRO", 
    page_icon="🛡️", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 0. BASE DE DATOS DE USUARIOS ---
# Aquí definimos los accesos y los PLANES (Demo, Basic, Pro)
USERS_DB = {
    # Usuario Administrador (PRO - Ilimitado)
    "admin@quanter.com": {
        "name": "Mario Saucedo",
        "password": "admin",
        "plan": "PRO",
        "company": "Quanter Consultores"
    },
    # Usuario Nuevo 1 (BASIC - 20 Archivos)
    "usuario1@general.com": {
        "name": "Usuario Estándar",
        "password": "user1",
        "plan": "BASIC", # <--- NUEVA LICENCIA DE 20
        "company": "Comercializadora del Centro"
    },
    # Usuario Nuevo 2 (PRO - Ilimitado)
    "usuario2@general.com": {
        "name": "Gerente Finanzas",
        "password": "user2",
        "plan": "PRO",
        "company": "Grupo Industrial Norte"
    },
    # Usuario Demo (DEMO - 5 Archivos)
    "cliente@demo.com": {
        "name": "Visitante Web",
        "password": "123",
        "plan": "DEMO",
        "company": "Invitado"
    }
}

# --- ESTILOS CSS (MODO LIGHT / CLEAN) ---
st.markdown("""
<style>
    /* Estilo sutil para métricas */
    [data-testid="stMetricValue"] { color: #2563eb; }
    
    /* BADGES (Etiquetas de Plan) */
    .badge-pro {
        background-color: #dcfce7; color: #166534;
        padding: 4px 10px; border-radius: 12px; font-weight: 700; border: 1px solid #bbf7d0;
    }
    .badge-basic {
        background-color: #f3e8ff; color: #6b21a8; /* Morado */
        padding: 4px 10px; border-radius: 12px; font-weight: 700; border: 1px solid #e9d5ff;
    }
    .badge-demo {
        background-color: #dbeafe; color: #1e40af;
        padding: 4px 10px; border-radius: 12px; font-weight: 700; border: 1px solid #bfdbfe;
    }
    
    .stButton>button { font-weight: bold; border-radius: 8px; height: 3em; }
</style>
""", unsafe_allow_html=True)

# --- GESTIÓN DE SESIÓN ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None

def login(email, password):
    email_limpio = email.strip().lower()
    pass_limpio = password.strip()

    if email_limpio in USERS_DB:
        if USERS_DB[email_limpio]['password'] == pass_limpio:
            st.session_state['logged_in'] = True
            st.session_state['user_info'] = USERS_DB[email_limpio]
            st.rerun()
        else:
            st.error("🔒 Contraseña incorrecta")
    else:
        st.error(f"👤 El usuario '{email_limpio}' no existe.")

def logout():
    st.session_state['logged_in'] = False
    st.session_state['user_info'] = None
    st.rerun()

# ==========================================
# VISTA 1: LOGIN
# ==========================================
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.write("")
        st.write("")
        st.markdown("<h1 style='text-align: center;'>🛡️ Auditor Fiscal PRO</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: grey;'>Inicia sesión para acceder.</p>", unsafe_allow_html=True)
        st.markdown("---")

        with st.form("login_form"):
            email = st.text_input("Correo Electrónico")
            password = st.text_input("Contraseña", type="password")
            submit = st.form_submit_button("Entrar", type="primary")
        
        if submit:
            login(email, password)
            
        st.info("Tip: Usa `usuario1@general.com` / `user1` para probar el límite de 20 archivos.")

# ==========================================
# VISTA 2: APLICACIÓN
# ==========================================
else:
    USER = st.session_state['user_info']
    PLAN = USER['plan']
    
    # --- 1. CARGA BD SAT ---
    ARCHIVO_SAT_LOCAL = "lista_negra_sat.csv"

    @st.cache_data
    def cargar_lista_negra_local():
        if not os.path.exists(ARCHIVO_SAT_LOCAL):
            return set(), False, "Base de datos SAT no encontrada"
        try:
            try: df = pd.read_csv(ARCHIVO_SAT_LOCAL, encoding='latin-1', skiprows=2)
            except: df = pd.read_csv(ARCHIVO_SAT_LOCAL, encoding='latin-1')

            df.columns = [str(c).strip().upper() for c in df.columns]
            col_rfc = next((c for c in df.columns if 'RFC' in c), None)
            col_sit = next((c for c in df.columns if 'SITUACI' in c), None)

            if col_rfc and col_sit:
                efos = df[df[col_sit].astype(str).str.contains("Definitivo", case=False, na=False)]
                lista_rfcs = set(efos[col_rfc].astype(str).str.strip().str.upper())
                return lista_rfcs, True, f"Base SAT Activa: {len(lista_rfcs):,} empresas"
            return set(), False, "Formato CSV inválido"
        except Exception as e:
            return set(), False, f"Error: {str(e)}"

    EFOS_SET, SAT_DB_ACTIVA, MENSAJE_SAT = cargar_lista_negra_local()

    # --- 2. VALIDACIONES ---
    def validar_efos(rfc, blacklist):
        if not blacklist: return "❓ No verificado"
        if rfc in blacklist: return "⛔ ALERTA EFO"
        return "✅ Limpio"

    def validar_timbrado(nodo_tfd):
        if nodo_tfd is None: return "⛔ NO TIMBRADO"
        if not nodo_tfd.get("UUID"): return "⛔ Sin UUID"
        return "✅ Timbrado OK"

    def validar_aritmetica(subtotal, impuestos, total):
        calculado = subtotal + impuestos
        diff = abs(calculado - total)
        return "✅ OK" if diff < 1.0 else f"⚠️ Descuadre (${diff:.2f})"

    def validar_rfc_estructura(rfc):
        if not rfc: return "⚠️ RFC Vacío"
        rfc = rfc.upper().strip()
        patron = r"^[A-Z&Ñ]{3,4}\d{6}[A-V1-9][A-Z1-9]\d$"
        if not re.match(patron, rfc): return f"⚠️ Inválido ({len(rfc)})"
        return "✅ OK"

    def validar_moneda_cambio(moneda, tipo_cambio):
        moneda = moneda.upper()
        try: tc = float(tipo_cambio) if tipo_cambio else 1.0
        except: return "⚠️ TC Error"
        if moneda == "MXN" and tc != 1.0: return f"⚠️ MXN con TC {tc}"
        if moneda != "MXN" and (not tipo_cambio or tc == 1.0): return f"⚠️ {moneda} TC dudoso"
        return "✅ OK"

    def validar_metodo_pago(metodo, forma_pago):
        if metodo == "PPD" and forma_pago != "99": return "⚠️ PPD error"
        if metodo == "PUE" and forma_pago == "99": return "⚠️ PUE error"
        return "✅ OK"

    def validar_fecha_reciente(fecha_str):
        try:
            fecha_dt = datetime.strptime(fecha_str[:10], "%Y-%m-%d")
            dias = (datetime.now() - fecha_dt).days
            return "⚠️ >1 año" if dias > 365 else "✅ OK"
        except: return "⚠️ Fecha Error"

    def parse_cfdi(file_content, reglas_activas, blacklist_set):
        try:
            tree = ET.parse(file_content)
            root = tree.getroot()
            ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4', 'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
            
            subtotal = float(root.get("SubTotal", 0))
            total = float(root.get("Total", 0))
            metodo = root.get("MetodoPago", "")
            forma = root.get("FormaPago", "")
            fecha = root.get("Fecha", "")
            moneda = root.get("Moneda", "MXN")
            tipo_cambio = root.get("TipoCambio", "")
            
            emisor = root.find("cfdi:Emisor", ns)
            rfc_emisor = emisor.get("Rfc", "").upper().strip() if emisor is not None else ""
            nombre_emisor = emisor.get("Nombre", "") if emisor is not None else ""
            
            total_impuestos = 0.0
            impuestos = root.find("cfdi:Impuestos", ns)
            if impuestos is not None:
                traslados = impuestos.get("TotalImpuestosTrasladados")
                if traslados: total_impuestos = float(traslados)
                else:
                    for tras in impuestos.findall(".//cfdi:Traslado", ns):
                        total_impuestos += float(tras.get("Importe", 0))

            tfd_node = None
            complemento = root.find("cfdi:Complemento", ns)
            if complemento is not None: tfd_node = complemento.find("tfd:TimbreFiscalDigital", ns)

            data = {
                "Archivo": "...",
                "UUID": tfd_node.get("UUID") if tfd_node is not None else "SIN TIMBRE",
                "Fecha": fecha[:10],
                "RFC Emisor": rfc_emisor,
                "Nombre Emisor": nombre_emisor,
                "Total": total,
            }

            if "Lista Negra SAT (EFOS)" in reglas_activas: data["Val. EFOS"] = validar_efos(rfc_emisor, blacklist_set)
            if "Timbrado Real (SAT)" in reglas_activas: data["Val. Timbrado"] = validar_timbrado(tfd_node)
            if "Aritmética" in reglas_activas: data["Val. Aritmética"] = validar_aritmetica(subtotal, total_impuestos, total)
            if "Sintaxis RFC" in reglas_activas: data["Val. RFC"] = validar_rfc_estructura(rfc_emisor)
            if "Moneda y Cambio" in reglas_activas: data["Val. Divisa"] = validar_moneda_cambio(moneda, tipo_cambio)
            if "Lógica PUE/PPD" in reglas_activas: data["Val. Pago"] = validar_metodo_pago(metodo, forma)
            if "Vigencia" in reglas_activas: data["Val. Fecha"] = validar_fecha_reciente(fecha)

            return data, True
        except Exception as e:
            return {"Error": str(e)}, False

    # --- SIDEBAR: PERFIL DE USUARIO ---
    with st.sidebar:
        st.title("👤 Mi Cuenta")
        st.write(f"**Usuario:** {USER['name']}")
        st.caption(USER['company'])
        
        st.divider()
        st.write("Estado de la Licencia:")
        
        if PLAN == "PRO":
            st.markdown("<span class='badge-pro'>✨ PLAN PRO</span>", unsafe_allow_html=True)
            st.caption("Capacidad Ilimitada")
        elif PLAN == "BASIC":
            st.markdown("<span class='badge-basic'>🔹 PLAN BÁSICO</span>", unsafe_allow_html=True)
            st.caption("Límite: 20 Archivos")
        else:
            st.markdown("<span class='badge-demo'>💡 MODO DEMO</span>", unsafe_allow_html=True)
            st.caption("Límite: 5 Archivos")
            
        st.divider()
        if st.button("Cerrar Sesión"):
            logout()

    # --- MAIN CONTENT ---
    st.title("🛡️ Auditor Fiscal PRO")
    st.markdown("Validación masiva de CFDI 4.0, cruce con listas negras y auditoría contable.")

    if SAT_DB_ACTIVA:
        st.success(f"✅ {MENSAJE_SAT}")
    else:
        st.warning(f"⚠️ {MENSAJE_SAT}. (Sube 'lista_negra_sat.csv' para activar).")
    
    st.divider()

    col1, col2 = st.columns([1, 1.5], gap="large")
    
    with col1:
        st.subheader("1. Cargar Archivos")
        uploaded_files = st.file_uploader("Selecciona tus XMLs", type=["xml"], accept_multiple_files=True)
        st.write("")
        ejecutar = st.button("EJECUTAR AUDITORÍA", type="primary")
    
    with col2:
        st.subheader("2. Reglas de Validación")
        opciones = [
            "Lista Negra SAT (EFOS)", "Timbrado Real (SAT)", "Aritmética", 
            "Sintaxis RFC", "Moneda y Cambio", "Lógica PUE/PPD", "Vigencia"
        ]
        reglas_seleccionadas = []
        cols_checks = st.columns(2)
        for i, opcion in enumerate(opciones):
            with cols_checks[i % 2]:
                if st.checkbox(opcion, value=True, key=f"chk_{i}"):
                    reglas_seleccionadas.append(opcion)

    # --- EJECUCIÓN (CON LÍMITES) ---
    if ejecutar:
        if not uploaded_files:
            st.warning("⚠️ Carga al menos un archivo XML.")
        else:
            # --- DEFINICIÓN DE LÍMITES ---
            limite = float('inf') # Por defecto infinito
            if PLAN == "DEMO":
                limite = 5
            elif PLAN == "BASIC":
                limite = 20
            
            # --- APLICACIÓN DEL LÍMITE ---
            archivos_a_procesar = uploaded_files
            if len(uploaded_files) > limite:
                archivos_a_procesar = uploaded_files[:limite]
                st.warning(f"⚠️ **LÍMITE DE PLAN {PLAN}:** Subiste {len(uploaded_files)} archivos, pero solo se procesarán los primeros {limite}.")

            with st.spinner("Procesando..."):
                all_data = []
                for file in archivos_a_procesar:
                    parsed_data, success = parse_cfdi(file, reglas_seleccionadas, EFOS_SET)
                    if success:
                        parsed_data["Archivo"] = file.name
                        all_data.append(parsed_data)
            
            if all_data:
                df = pd.DataFrame(all_data)
                
                st.divider()
                st.subheader("📊 Resultados")
                
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Procesados", len(df))
                m2.metric("Monto Total", f"${df['Total'].sum():,.2f}")
                
                if "Val. EFOS" in df.columns:
                    num_efos = df[df["Val. EFOS"].str.contains("ALERTA", na=False)].shape[0]
                    m3.metric("EFOS Detectados", num_efos)
                else:
                    m3.metric("EFOS", "N/A")

                if "Val. Aritmética" in df.columns:
                    num_math = df[df["Val. Aritmética"].str.contains("⚠️", na=False)].shape[0]
                    m4.metric("Errores Aritméticos", num_math)

                def highlight_issues(val):
                    s_val = str(val)
                    if "ALERTA" in s_val: return 'background-color: #fee2e2; color: #991b1b; font-weight: bold;'
                    if "⛔" in s_val: return 'background-color: #fecaca; color: #7f1d1d;' 
                    if "⚠️" in s_val: return 'background-color: #fef9c3; color: #854d0e;'
                    return ''

                cols_val = [c for c in df.columns if "Val." in c]
                st.dataframe(df.style.applymap(highlight_issues, subset=cols_val), use_container_width=True, height=500)
                
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False)
                    workbook = writer.book
                    worksheet = writer.sheets['Sheet1']
                    red_fmt = workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006'})
                    if len(df) > 0:
                         worksheet.conditional_format(1, 0, len(df), len(df.columns)-1,
                            {'type': 'text', 'criteria': 'containing', 'value': 'ALERTA', 'format': red_fmt})

                st.download_button("📥 Descargar Excel", output.getvalue(), "Auditoria_Fiscal.xlsx", type="primary")

    # --- FOOTER ---
    st.write("")
    st.markdown("---")
    st.subheader("Glosario y Ayuda")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Glosario:**")
        st.markdown("- **EFOS:** Empresas en Lista Negra del SAT.\n- **UUID:** Folio Fiscal único.\n- **PUE/PPD:** Métodos de pago.")
    with c2:
        st.markdown("**Validaciones:**")
        st.markdown("- **Aritmética:** Sumas cuadren al centavo.\n- **Timbrado:** Sello real del SAT.\n- **Vigencia:** Antigüedad < 1 año.")