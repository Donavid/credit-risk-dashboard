import pandas as pd
import ssl # <--- Agrega esta librería
# <--- Agrega esta línea mágica para saltar el bloqueo SSL
ssl._create_default_https_context = ssl._create_unverified_context 
from sqlalchemy import create_engine
# 1. CONFIGURACIÓN DE LA CONEXIÓN (Igual que en DBeaver)
DB_USER = 'donar'
DB_PASS = 'password123'
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'riesgo_credito'

# Creamos el "motor" que conecta Python con SQL
engine = create_engine(f'postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}')

def ejecutar_etl():
    print("⏳ Paso 1: Descargando datos del servidor (Dataset German Credit)...")
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/statlog/german/german.data"
    
    # Definimos los nombres de las columnas (estaban ocultas en el archivo original)
    columnas = ['status_checking', 'duration', 'credit_history', 'purpose',
               'amount', 'savings', 'employment', 'installment_rate',
               'personal_status', 'guarantors', 'residence_since', 'property',
               'age', 'other_plans', 'housing', 'num_credits',
               'job', 'people_liable', 'telephone', 'foreign_worker', 'default_status']
    
    # Leemos el archivo como si fuera un Excel
    df = pd.read_csv(url, sep=' ', names=columnas)

    print("⏳ Paso 2: Limpiando y transformando datos...")
    
    # REGLA DE NEGOCIO: El dataset original usa 1=Bueno, 2=Malo.
    # Lo cambiamos a 0=Al día, 1=Default (Estándar bancario para facilitar sumas)
    df['is_default'] = df['default_status'].apply(lambda x: 1 if x == 2 else 0)
    
    # TRADUCCIÓN TÉCNICA: Códigos crudos a palabras reales
    mapa_proposito = {
        'A40': 'Vehículo Nuevo', 'A41': 'Vehículo Usado', 
        'A42': 'Mobiliario', 'A43': 'Radio/TV', 
        'A46': 'Educación', 'A49': 'Negocios', 'A410': 'Otros'
    }
    # Si el código no está en el mapa, ponemos 'Consumo General'
    df['purpose_txt'] = df['purpose'].map(mapa_proposito).fillna('Consumo General')

    print(f"✅ Datos listos: {len(df)} créditos procesados.")

    print("⏳ Paso 3: Guardando en Base de Datos...")
    # if_exists='replace' significa que si corres esto dos veces, borra y crea de nuevo (ideal para pruebas)
    df.to_sql('tabla_creditos', engine, if_exists='replace', index=False)
    
    print("🚀 ¡ETL Finalizado! Revisa DBeaver.")

if __name__ == "__main__":
    ejecutar_etl()