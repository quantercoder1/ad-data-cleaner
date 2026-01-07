import pandas as pd
import os
import numpy as np

# Crear carpeta para los archivos
output_folder = "test_files"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

print(f"📂 Generando archivos en: {output_folder} ...")

# --- ESCENARIO 1: E-COMMERCE SIMPLE (CSV) ---
# Prueba básica: Email sucio, Teléfono con guiones, Columnas de dinero que deben preservarse.
data1 = {
    "Order_ID": [101, 102, 103, 104, 105],
    "Customer_Email": [" JUAN@GMAIL.COM ", "maria.perez@hotmail.com", "  info@empresa.mx", "PEDRO@YAHOO.COM", "luis.test@gmail.com"],
    "Mobile_Phone": ["555-123-4567", "(81) 8345-6789", "55 4433 2211", "+52 1 55 9999 0000", "5551112222"],
    "Total_Spent": [1500.50, 200.00, 5000.00, 45.90, 120.00],
    "Currency": ["MXN", "MXN", "MXN", "USD", "MXN"]
}
df1 = pd.DataFrame(data1)
df1.to_csv(f"{output_folder}/1_ecommerce_simple.csv", index=False)
print("✅ 1_ecommerce_simple.csv creado.")

# --- ESCENARIO 2: LEAD GENERATION (XLSX) ---
# Prueba: Muchos datos extra (Source, Campaign), Teléfonos con extensiones o texto.
data2 = {
    "Lead_Date": ["2025-01-01", "2025-01-02", "2025-01-03", "2025-01-04"],
    "Full_Name": ["Ana Lopez", "Beto Diaz", "Carla Ruiz", "Dani Fox"],
    "Contact_Email": ["ana.lopez@agency.com", "beto.d@startup.io", "carla@ruiz.net", "dani@fox.com"],
    "Phone_Number": ["Tel: 55-1234-5678", "Ext. 404", "818-765-4321", "N/A"],
    "Source": ["Facebook Ads", "Google Ads", "Referral", "LinkedIn"],
    "Campaign_ID": ["Q1_PROMO", "Q1_PROMO", "EVERGREEN", "COLD_OUTREACH"]
}
df2 = pd.DataFrame(data2)
df2.to_excel(f"{output_folder}/2_leads_marketing.xlsx", index=False)
print("✅ 2_leads_marketing.xlsx creado.")

# --- ESCENARIO 3: BASE DE DATOS VIEJA (CSV) ---
# Prueba: Columnas en español, Emails faltantes (NaN), teléfonos mezclados.
data3 = {
    "ID_Cliente": ["C-001", "C-002", "C-003", "C-004", "C-005"],
    "Nombre": ["Empresa A", "Empresa B", "Empresa C", "Empresa D", "Empresa E"],
    "Correo_Electronico": ["contacto@a.com", np.nan, "ventas@c.com", "admin@d.com", ""], # Ojo con los vacíos
    "Celular": ["5511223344", "8112233445", "", "3312345678", "5598765432"],
    "Direccion": ["Calle 1", "Av Reforma", "Calle 5", "Blvd Norte", "Centro"],
    "Notas": ["Cliente VIP", "Moroso", "Nuevo", "Contactar mañana", "Baja"]
}
df3 = pd.DataFrame(data3)
df3.to_csv(f"{output_folder}/3_legacy_db_messy.csv", index=False)
print("✅ 3_legacy_db_messy.csv creado.")

# --- ESCENARIO 4: CLIENTES INTERNACIONALES (XLSX) ---
# Prueba: Caracteres internacionales, teléfonos largos.
data4 = {
    "User": ["User1", "User2", "User3"],
    "E-mail Address": ["john.doe@usa.com", "hans.mueller@germany.de", "pierre@france.fr"],
    "Phone (Intl)": ["+1 415 555 0100", "+49 30 123456", "+33 1 23 45 67 89"],
    "Country": ["USA", "Germany", "France"],
    "Plan": ["Premium", "Basic", "Enterprise"]
}
df4 = pd.DataFrame(data4)
df4.to_excel(f"{output_folder}/4_international_clients.xlsx", index=False)
print("✅ 4_international_clients.xlsx creado.")

# --- ESCENARIO 5: SOLO EMAIL (CSV) ---
# Prueba: Qué pasa si NO seleccionas columna de teléfono (el script debe aguantar).
data5 = {
    "Subscriber": ["Sub1", "Sub2", "Sub3", "Sub4"],
    "Email_List": [" NEWSLETTER@BLOG.COM", "fan1@gmail.com", "fan2@hotmail.com ", "ERROR_EMAIL"],
    "Status": ["Active", "Active", "Unsubscribed", "Active"]
}
df5 = pd.DataFrame(data5)
df5.to_csv(f"{output_folder}/5_newsletter_only_email.csv", index=False)
print("✅ 5_newsletter_only_email.csv creado.")

# --- ESCENARIO 6: FORMATO COMPLEJO (XLSX) ---
# Prueba: Muchas columnas numéricas que no deben romperse.
data6 = {
    "SKU": ["A100", "B200", "C300"],
    "Product": ["Laptop", "Mouse", "Keyboard"],
    "Buyer_Email": ["tech@store.com", "gamer@home.com", "office@work.com"],
    "Buyer_Phone": ["55-0000-1111", "55-0000-2222", "55-0000-3333"],
    "Cost": [800, 20, 50],
    "Price": [1200, 40, 80],
    "Margin": [400, 20, 30],
    "Tax": [0.16, 0.16, 0.16],
    "Warehouse": ["CDMX", "MTY", "GDL"]
}
df6 = pd.DataFrame(data6)
df6.to_excel(f"{output_folder}/6_inventory_sales.xlsx", index=False)
print("✅ 6_inventory_sales.xlsx creado.")

print("\n🚀 ¡Listo! Revisa la carpeta 'test_files' en tu directorio actual.")