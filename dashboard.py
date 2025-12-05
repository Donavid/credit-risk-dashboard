import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px

# 1. CONFIGURACIÓN DE PÁGINA
st.set_page_config(page_title="Tablero de Riesgo", layout="wide")

# 2. CONEXIÓN A BASE DE DATOS (La misma que usaste antes)
def cargar_datos():
    # Conectamos a tu Docker
    engine = create_engine('postgresql://donar:password123@localhost:5432/riesgo_credito')
    
    # ¡Aquí ocurre la magia! Leemos directamente la VISTA que creaste en DBeaver
    query = "SELECT * FROM vista_reporte_riesgo"
    df = pd.read_sql(query, engine)
    return df

# Cargamos los datos
df = cargar_datos()

# 3. INTERFAZ GRÁFICA (El Frontend)
st.title("🏦 Dashboard de Riesgo Crediticio")
st.markdown("---")

# Métrica Principal (KPIs Totales)
col1, col2, col3 = st.columns(3)
total_creditos = df['cantidad_creditos'].sum()
monto_cartera = df['volumen_total'].sum()
promedio_morosidad = df['tasa_morosidad'].mean()

col1.metric("Total Créditos", f"{total_creditos}")
col2.metric("Volumen de Cartera", f"${monto_cartera:,.0f}")
col3.metric("Tasa Morosidad Promedio", f"{promedio_morosidad:.2f}%")

st.markdown("---")

# 4. GRÁFICOS INTERACTIVOS

# Dividimos la pantalla en dos columnas para gráficos
c1, c2 = st.columns(2)

with c1:
    st.subheader("🔍 Morosidad por Producto")
    # Gráfico de Barras: ¿Qué producto tiene más riesgo?
    fig_bar = px.bar(df, x='producto', y='tasa_morosidad', 
                     color='tasa_morosidad',
                     title="Tasa de Default por Tipo de Crédito",
                     color_continuous_scale='Reds')
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    st.subheader("👥 Distribución por Segmento")
    # Gráfico de Torta: ¿Quiénes son nuestros clientes?
    df_segmento = df.groupby('segmento_cliente')['cantidad_creditos'].sum().reset_index()
    fig_pie = px.pie(df_segmento, names='segmento_cliente', values='cantidad_creditos',
                     title="Cantidad de Créditos por Edad")
    st.plotly_chart(fig_pie, use_container_width=True)

# 5. MOSTRAR LA TABLA DETALLADA (Lo que veías en DBeaver)
st.markdown("### 📋 Detalle de Cartera")
st.dataframe(df)