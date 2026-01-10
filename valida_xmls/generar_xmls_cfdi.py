import os
import random
import datetime

# Configuración
OUTPUT_FOLDER = "test_xmls_cfdi"
CANTIDAD = 100

if not os.path.exists(OUTPUT_FOLDER):
    os.makedirs(OUTPUT_FOLDER)

print(f"📂 Generando {CANTIDAD} archivos XML (CFDI 4.0 Simulado) en '{OUTPUT_FOLDER}'...")

# --- DATOS DE PRUEBA ---
rfcs_emisores = ["AAA010101AAA", "GOMJ880101L99", "QUAN260101XYZ", "SAT970701NN3"]
nombres_emisores = ["Empresa Demo SA de CV", "Juan Perez S.A.", "Quanter Consultores", "Servicios SAT"]
rfcs_receptores = ["XAXX010101000", "XEXX010101000", "GME050505R55", "CLI990909QR9"]

descripciones = [
    "Servicio de consultoría de software", 
    "Licencia anual SaaS", 
    "Mantenimiento de servidores", 
    "Curso de capacitación Python", 
    "Venta de equipo de cómputo"
]

def generar_fecha():
    """Genera una fecha reciente en formato ISO 8601"""
    inicio = datetime.datetime(2025, 1, 1)
    dias = random.randint(0, 365)
    fecha = inicio + datetime.timedelta(days=dias)
    return fecha.strftime("%Y-%m-%dT%H:%M:%S")

def generar_xml_string(index):
    # Datos aleatorios para este archivo
    serie = random.choice(["A", "F", "NOM", "B"])
    folio = 1000 + index
    fecha = generar_fecha()
    subtotal = round(random.uniform(1000.00, 50000.00), 2)
    iva = round(subtotal * 0.16, 2)
    total = round(subtotal + iva, 2)
    
    rfc_emisor = random.choice(rfcs_emisores)
    nombre_emisor = random.choice(nombres_emisores)
    rfc_receptor = random.choice(rfcs_receptores)
    
    descripcion = random.choice(descripciones)

    # Estructura CFDI 4.0 (Simulada pero válida en estructura)
    xml_content = f"""<?xml version="1.0" encoding="utf-8"?>
<cfdi:Comprobante xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:cfdi="http://www.sat.gob.mx/cfd/4" Version="4.0" Serie="{serie}" Folio="{folio}" Fecha="{fecha}" Sello="SIMULACION_DE_SELLO_DIGITAL_SHA256_BASE64..." FormaPago="99" NoCertificado="00001000000505050505" SubTotal="{subtotal}" Moneda="MXN" Total="{total}" TipoDeComprobante="I" Exportacion="01" MetodoPago="PUE" LugarExpedicion="20000">
  <cfdi:Emisor Rfc="{rfc_emisor}" Nombre="{nombre_emisor}" RegimenFiscal="601"/>
  <cfdi:Receptor Rfc="{rfc_receptor}" Nombre="CLIENTE GENERICO SA DE CV" DomicilioFiscalReceptor="20000" RegimenFiscalReceptor="601" UsoCFDI="G03"/>
  <cfdi:Conceptos>
    <cfdi:Concepto ClaveProdServ="80101500" Cantidad="1" ClaveUnidad="E48" Unidad="Servicio" Descripcion="{descripcion}" ValorUnitario="{subtotal}" Importe="{subtotal}" ObjetoImp="02">
      <cfdi:Impuestos>
        <cfdi:Traslados>
          <cfdi:Traslado Base="{subtotal}" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="{iva}"/>
        </cfdi:Traslados>
      </cfdi:Impuestos>
    </cfdi:Concepto>
  </cfdi:Conceptos>
  <cfdi:Impuestos TotalImpuestosTrasladados="{iva}">
    <cfdi:Traslados>
      <cfdi:Traslado Base="{subtotal}" Impuesto="002" TipoFactor="Tasa" TasaOCuota="0.160000" Importe="{iva}"/>
    </cfdi:Traslados>
  </cfdi:Impuestos>
</cfdi:Comprobante>"""
    return xml_content

# Generar los 100 archivos
for i in range(CANTIDAD):
    contenido = generar_xml_string(i)
    nombre_archivo = f"{OUTPUT_FOLDER}/factura_{i+1}.xml"
    
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        f.write(contenido)

print(f"✅ ¡Listo! Se crearon 100 archivos XML en la carpeta '{OUTPUT_FOLDER}'.")