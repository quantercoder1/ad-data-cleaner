import pandas as pd
import random
import os
import numpy as np

# Crear carpeta para los archivos masivos
output_folder = "test_files_large"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

print(f"🚀 Iniciando generación masiva en: {output_folder} ...")

# --- UTILIDADES PARA GENERAR CAOS ---
dominios = ["gmail.com", "HOTMAIL.COM", "yahoo.com", "outlook.com", "empresa.mx", "agency.io"]
nombres = ["Juan", "Maria", "Pedro", "Luisa", "Carlos", "Ana", "Beto", "Sofia", "Miguel", "Diana"]
apellidos = ["Perez", "Gomez", "Lopez", "Diaz", "Ruiz", "Hernandez", "Smith", "Garcia", "Martinez"]

def generar_email_sucio():
    """Genera un email con probabilidad de estar sucio (espacios, mayúsculas) o vacío"""
    if random.random() < 0.05: return np.nan  # 5% de probabilidad de ser Nulo real
    if random.random() < 0.05: return ""      # 5% de probabilidad de ser vacío string
    
    nombre = random.choice(nombres)
    apellido = random.choice(apellidos)
    dominio = random.choice(dominios)
    email = f"{nombre}.{apellido}@{dominio}"
    
    # Ensuciar
    caso = random.randint(1, 4)
    if caso == 1: return email.upper() # TODO MAYUSCULAS
    if caso == 2: return f"  {email} " # Espacios extra
    if caso == 3: return email.replace("@", " @") # Error tipico
    return email.lower()

def generar_telefono_sucio():
    """Genera teléfonos con formatos variados"""
    if random.random() < 0.1: return np.nan # 10% nulos
    
    nums = f"{random.randint(100,999)}{random.randint(1000000,9999999)}"
    caso = random.randint(1, 5)
    
    if caso == 1: return f"55-{nums[:4]}-{nums[4:]}"      # Con guiones
    if caso == 2: return f"({nums[:3]}) {nums[3:6]} {nums[6:]}" # Con paréntesis
    if caso == 3: return f"+52 1 {nums}"                 # Formato intl
    if caso == 4: return f"Tel: {nums} Ext 123"          # Con texto basura
    return nums # Limpio

# ==========================================
# ARCHIVO 1: 1,000 REGISTROS (CSV) - E-commerce
# ==========================================
print("⚡ Generando Dataset 1 (1,000 filas)...")
data1 = []
for i in range(1000):
    data1.append({
        "Order_ID": f"ORD-{1000+i}",
        "Customer_Name": f"{random.choice(nombres)} {random.choice(apellidos)}",
        "Buyer_Email": generar_email_sucio(),
        "Contact_Phone": generar_telefono_sucio(),
        "Total_Paid": round(random.uniform(50.0, 5000.0), 2),
        "Status": random.choice(["Paid", "Pending", "Refunded"])
    })

df1 = pd.DataFrame(data1)
df1.to_csv(f"{output_folder}/1k_ecommerce_users.csv", index=False)
print("✅ 1k_ecommerce_users.csv creado.")

# ==========================================
# ARCHIVO 2: 2,000 REGISTROS (XLSX) - Leads Agencia
# ==========================================
print("⚡ Generando Dataset 2 (2,000 filas)...")
data2 = []
for i in range(2000):
    data2.append({
        "Lead_ID": i + 1,
        "Date": "2026-01-07",
        "Campaign_Source": random.choice(["Facebook", "Google", "TikTok", "Organic"]),
        "Target_Email": generar_email_sucio(),
        "Target_Phone": generar_telefono_sucio(),
        "User_ID_CRM": f"USER_{random.randint(10000, 99999)}", # Para probar la columna ID
        "Notes": "Interesado en demo"
    })

df2 = pd.DataFrame(data2)
df2.to_excel(f"{output_folder}/2k_agency_leads.xlsx", index=False)
print("✅ 2k_agency_leads.xlsx creado.")

# ==========================================
# ARCHIVO 3: 3,000 REGISTROS (CSV) - Base de Datos Pesada
# ==========================================
print("⚡ Generando Dataset 3 (3,000 filas)...")
data3 = []
for i in range(3000):
    data3.append({
        "DB_Index": i,
        "Raw_Email_String": generar_email_sucio(),
        "Mobile_Number_V2": generar_telefono_sucio(),
        "Legacy_ID": f"OLD-{random.randint(100,999)}",
        "Region": random.choice(["North", "South", "East", "West"]),
        "Is_Active": random.choice([True, False]),
        "Last_Login": "2025-12-31"
    })

df3 = pd.DataFrame(data3)
# Insertamos un caso trampa específico para probar tu parche de seguridad
df3.at[100, "Raw_Email_String"] = "nan" # Texto literal 'nan'
df3.at[101, "Raw_Email_String"] = None  # Nulo real

df3.to_csv(f"{output_folder}/3k_legacy_database.csv", index=False)
print("✅ 3k_legacy_database.csv creado.")

print("\n🎉 ¡Generación Masiva Completa! Revisa la carpeta 'test_files_large'")