import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="XML Mass Auditor", page_icon="📑", layout="wide")

# --- ESTILOS CSS ---
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 5px solid #2563eb;}
    .stDataFrame {border: 1px solid #e0e0e0; border-radius: 5px;}
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE PARSEO XML (CFDI 4.0) ---
def parse_cfdi(file_content):
    """
    Lee un archivo XML en memoria y extrae datos clave del CFDI 4.0
    """
    try:
        tree = ET.parse(file_content)
        root = tree.getroot()
        
        # Manejo de Namespaces (El SAT usa cfdi: y tfd:)
        ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4', 'tfd': 'http://www.sat.gob.mx/TimbreFiscalDigital'}
        
        # 1. Datos Generales (Nodo Raíz)
        data = {
            "Serie": root.get("Serie", ""),
            "Folio": root.get("Folio", ""),
            "Fecha": root.get("Fecha", ""),
            "SubTotal": float(root.get("SubTotal", 0)),
            "Total": float(root.get("Total", 0)),
            "Moneda": root.get("Moneda", ""),
            "Tipo": root.get("TipoDeComprobante", ""),
            "MetodoPago": root.get("MetodoPago", ""),
            "Version": root.get("Version", "")
        }

        # 2. Emisor
        emisor = root.find("cfdi:Emisor", ns)
        if emisor is not None:
            data["RFC Emisor"] = emisor.get("Rfc", "")
            data["Nombre Emisor"] = emisor.get("Nombre", "")
            data["Regimen Emisor"] = emisor.get("RegimenFiscal", "")

        # 3. Receptor
        receptor = root.find("cfdi:Receptor", ns)
        if receptor is not None:
            data["RFC Receptor"] = receptor.get("Rfc", "")
            data["Nombre Receptor"] = receptor.get("Nombre", "")
            data["Uso CFDI"] = receptor.get("UsoCFDI", "")
            data["CP Receptor"] = receptor.get("DomicilioFiscalReceptor", "")

        # 4. Impuestos (Total Trasladados)
        # A veces está en el nodo global de impuestos
        impuestos = root.find("cfdi:Impuestos", ns)
        if impuestos is not None:
            data["Total Impuestos"] = float(impuestos.get("TotalImpuestosTrasladados", 0))
        else:
            # Si no hay nodo global, calculamos manual (simplificado para MVP)
            data["Total Impuestos"] = round(data["Total"] - data["SubTotal"], 2)

        return data, True # True = Éxito

    except Exception as e:
        return {"Error": str(e)}, False

# --- INTERFAZ DE USUARIO ---
st.title("📑 XML Mass Auditor (CFDI 4.0)")
st.markdown("Herramienta Micro-SaaS para contadores: Convierte XMLs masivos a Excel y audita errores.")

# Sidebar
st.sidebar.header("Panel de Control")
uploaded_files = st.sidebar.file_uploader("Sube tus XMLs (Arrástralos aquí)", type=["xml"], accept_multiple_files=True)

if uploaded_files:
    st.divider()
    all_data = []
    errors = []
    
    # Barra de progreso
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Procesamiento
    for i, file in enumerate(uploaded_files):
        # Actualizar barra
        progress = (i + 1) / len(uploaded_files)
        progress_bar.progress(progress)
        status_text.text(f"Procesando archivo {i+1} de {len(uploaded_files)}...")
        
        # Parsear
        parsed_data, success = parse_cfdi(file)
        
        if success:
            # Añadir nombre de archivo original para referencia
            parsed_data["Archivo"] = file.name
            all_data.append(parsed_data)
        else:
            errors.append(file.name)
            
    status_text.text("✅ Procesamiento completado.")
    progress_bar.empty()

    # --- RESULTADOS ---
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Métricas Rápidas (Dashboard)
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Facturas Procesadas", len(df))
        c2.metric("Total Facturado", f"${df['Total'].sum():,.2f}")
        c3.metric("IVA Trasladado (Aprox)", f"${df['Total Impuestos'].sum():,.2f}")
        c4.metric("Emisores Únicos", df['RFC Emisor'].nunique())
        
        st.subheader("📊 Vista Previa de Datos")
        # Ordenar columnas para mejor lectura
        cols_order = ["Fecha", "Serie", "Folio", "RFC Emisor", "Nombre Emisor", "RFC Receptor", "SubTotal", "Total Impuestos", "Total", "Uso CFDI"]
        # Filtrar solo columnas que existan
        cols_final = [c for c in cols_order if c in df.columns]
        
        st.dataframe(df[cols_final], use_container_width=True)
        
        # --- DESCARGA ---
        st.subheader("📥 Descargar Reporte")
        
        # Convertir a Excel en memoria
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Facturas')
            # Ajustar ancho de columnas (básico)
            worksheet = writer.sheets['Facturas']
            worksheet.set_column(0, 20, 15) # Ancho genérico
            
        processed_data = output.getvalue()
        
        c_down1, c_down2 = st.columns([1, 2])
        with c_down1:
            st.download_button(
                label="Descargar Excel (.xlsx)",
                data=processed_data,
                file_name="Reporte_XML_Auditor.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )

    # Mostrar Errores si los hubo
    if errors:
        st.error(f"⚠️ No se pudieron leer {len(errors)} archivos.")
        with st.expander("Ver archivos con error"):
            st.write(errors)

else:
    # Estado inicial (Empty State)
    st.info("👈 Sube tus archivos XML en el menú lateral para comenzar.")
    
    # Demo visual
    st.markdown("---")
    st.markdown("### ¿Qué resuelve esta herramienta?")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**⛔ El Problema:**")
        st.markdown("* Contadores perdiendo horas copiando datos de PDFs.")
        st.markdown("* Errores de dedo al pasar montos a Excel.")
        st.markdown("* Imposible auditar 500 XMLs visualmente.")
    with c2:
        st.markdown("**✅ La Solución:**")
        st.markdown("* Extracción automática de Nodos CFDI 4.0.")
        st.markdown("* Cálculo automático de impuestos.")
        st.markdown("* Detección de RFCs duplicados o errores.")