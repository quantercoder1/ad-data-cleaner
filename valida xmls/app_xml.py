import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from io import BytesIO

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="XML Auditor PRO", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .stDataFrame {border: 1px solid #e0e0e0; border-radius: 5px;}
    /* Resaltar errores en rojo suave */
    .error-row {background-color: #ffcccc;}
</style>
""", unsafe_allow_html=True)

# --- LÓGICA DE PARSEO ---
def parse_cfdi(file_content):
    try:
        tree = ET.parse(file_content)
        root = tree.getroot()
        ns = {'cfdi': 'http://www.sat.gob.mx/cfd/4'}
        
        # Extracción básica
        subtotal = float(root.get("SubTotal", 0))
        total = float(root.get("Total", 0))
        
        # Calcular impuestos (si existen)
        total_impuestos = 0.0
        impuestos = root.find("cfdi:Impuestos", ns)
        if impuestos is not None:
            # Intentar leer el total trasladado
            traslados = impuestos.get("TotalImpuestosTrasladados")
            if traslados:
                total_impuestos = float(traslados)
            else:
                # Si no hay atributo global, sumar manual (más preciso)
                for tras in impuestos.findall(".//cfdi:Traslado", ns):
                    total_impuestos += float(tras.get("Importe", 0))

        # --- VALIDACIÓN MATEMÁTICA ---
        # Calculamos cuánto debería ser
        calculado = subtotal + total_impuestos
        diferencia = abs(calculado - total)
        # Si la diferencia es mayor a 1 peso, hay error
        status_math = "✅ OK" if diferencia < 1.0 else f"⚠️ Descuadre (${diferencia:.2f})"

        data = {
            "UUID/Folio": root.get("Folio", "") or "S/N",
            "Fecha": root.get("Fecha", "")[:10], # Solo la fecha YYYY-MM-DD
            "RFC Emisor": root.find("cfdi:Emisor", ns).get("Rfc", ""),
            "Nombre Emisor": root.find("cfdi:Emisor", ns).get("Nombre", ""),
            "RFC Receptor": root.find("cfdi:Receptor", ns).get("Rfc", ""),
            "Metodo Pago": root.get("MetodoPago", ""),
            "Forma Pago": root.get("FormaPago", ""),
            "SubTotal": subtotal,
            "Impuestos": total_impuestos,
            "Total XML": total,
            "Validación Aritmética": status_math # Nueva columna de poder
        }
        return data, True

    except Exception as e:
        return {"Error": str(e)}, False

# --- UI PRINCIPAL ---
st.title("🛡️ XML Auditor PRO")
st.markdown("Validador Masivo de CFDI 4.0: Integridad de datos y aritmética.")

# --- SIDEBAR MEJORADO ---
st.sidebar.header("Carga de Archivos")
uploaded_files = st.sidebar.file_uploader("Arrastra tus XMLs aquí", type=["xml"], accept_multiple_files=True)

if uploaded_files:
    all_data = []
    lista_archivos_ui = [] # Para el listado visual
    
    # Procesamiento silencioso (sin barra de progreso para máxima velocidad en UI)
    for file in uploaded_files:
        parsed_data, success = parse_cfdi(file)
        
        estado_icon = "✅" if success else "❌"
        lista_archivos_ui.append({"Archivo": file.name, "Estado": estado_icon})
        
        if success:
            parsed_data["Archivo"] = file.name
            all_data.append(parsed_data)
    
    # --- UI REQUEST 1: LISTA LARGA CON SCROLL ---
    st.sidebar.markdown("---")
    st.sidebar.subheader(f"Archivos ({len(uploaded_files)})")
    df_files = pd.DataFrame(lista_archivos_ui)
    # Height 400px permite ver unos 15-20 archivos con scroll
    st.sidebar.dataframe(df_files, use_container_width=True, hide_index=True, height=400)

    # --- RESULTADOS PRINCIPALES ---
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Métricas de Negocio
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Facturado", f"${df['Total XML'].sum():,.2f}")
        c2.metric("Impuestos Detectados", f"${df['Impuestos'].sum():,.2f}")
        # Métrica de Calidad
        errores_math = df[df["Validación Aritmética"].str.contains("⚠️")].shape[0]
        c3.metric("Errores Aritméticos", errores_math, delta_color="inverse")

        st.divider()
        st.subheader("🔍 Auditoría Detallada")
        
        # Ordenar columnas
        cols = ["Fecha", "RFC Emisor", "Nombre Emisor", "SubTotal", "Impuestos", "Total XML", "Validación Aritmética", "Metodo Pago", "Archivo"]
        
        # Dataframe con colores condicionales (Highlight errors)
        # Esto colorea de amarillo las celdas que tengan "⚠️"
        def highlight_warnings(val):
            color = '#ffeba8' if '⚠️' in str(val) else ''
            return f'background-color: {color}'

        st.dataframe(
            df[cols].style.applymap(highlight_warnings, subset=['Validación Aritmética']),
            use_container_width=True,
            height=500
        )
        
        # --- DESCARGA ---
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df[cols].to_excel(writer, index=False, sheet_name='Auditoria')
            # Formato condicional en Excel (Básico)
            workbook = writer.book
            worksheet = writer.sheets['Auditoria']
            format_currency = workbook.add_format({'num_format': '$#,##0.00'})
            worksheet.set_column('D:F', 15, format_currency) # Columnas de dinero
            
        st.download_button(
            "📥 Descargar Reporte Auditado (.xlsx)",
            data=output.getvalue(),
            file_name="Auditoria_Fiscal_XML.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary"
        )

else:
    st.info("👈 Carga tus XMLs para comenzar la auditoría.")