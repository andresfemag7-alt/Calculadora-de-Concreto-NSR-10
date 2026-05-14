import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import requests
# Importamos el diccionario de ubicaciones desde el archivo externo
from ubicaciones import lugares_colombia

"""
Función del programa: APLICACIÓN WEB PARA DISEÑO DE MEZCLAS DE CONCRETO
Autor: Ing. Civiles Andrés Felipe Madroñero Garces & José Manuel Arboleda Carvajal.
"""

st.set_page_config(page_title="Calculadora NSR-10", layout="wide")

# --- ESTILOS ---
def cargar_estilos_y_fondo():
    try:
        with open("fondo2.png", "rb") as image_file:
            imagen_base64 = base64.b64encode(image_file.read()).decode()
            
        css = f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{imagen_base64});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("Fondo no encontrado.")

cargar_estilos_y_fondo()

# --- LÓGICA DE CLIMA ---
def obtener_clima_por_ciudad(municipio):
    # Función para consultar el API de Open-Meteo
    try:
        params_geo = {"name": municipio, "count": 1, "language": "es"}
        url_geo = "https://geocoding-api.open-meteo.com/v1/search"
        respuesta_geo = requests.get(url_geo, params=params_geo).json()
        
        if "results" not in respuesta_geo or not respuesta_geo["results"]:
            return None, None, "Ciudad no encontrada."

        lat = respuesta_geo["results"][0]["latitude"]
        lon = respuesta_geo["results"][0]["longitude"]

        params_clima = {
            "latitude": lat, "longitude": lon,
            "daily": "precipitation_probability_max",
            "current_weather": "true", "timezone": "America/Bogota"
        }
        url_clima = "https://api.open-meteo.com/v1/forecast"
        datos = requests.get(url_clima, params=params_clima).json()
        
        return datos['current_weather']['temperature'], datos['daily']['precipitation_probability_max'][0], municipio
    except Exception as e:
        return None, None, f"Error: {e}"

# --- LÓGICA DE CÁLCULO ---
def calcular_mezcla(resistencia, volumen, unidades, marca, aditivo, recipiente, precios):
    # Convertimos a m3 para estandarizar el cálculo interno
    # Se usa precisión decimal alta para evitar el error de "proporciones en cero"
    volumen_m3 = volumen / 1000 if unidades == "Litros (L)" else volumen

    # Dosificación teórica por m3 (NSR-10 simplificada)
    if resistencia == "2500 PSI":
        cem_kg, arena_m3, trit_m3, agua_l = 300, 0.50, 0.70, 170
    elif resistencia == "3000 PSI":
        cem_kg, arena_m3, trit_m3, agua_l = 350, 0.45, 0.70, 180
    else: # 4000 PSI
        cem_kg, arena_m3, trit_m3, agua_l = 420, 0.40, 0.70, 200

    # Escalar valores al volumen solicitado
    cem_total = cem_kg * volumen_m3
    arena_total = arena_m3 * volumen_m3
    trit_total = trit_m3 * volumen_m3
    agua_total = agua_l * volumen_m3

    # Lógica de aditivos (dosificación por peso de cemento)
    vol_aditivo_L = 0
    porcentajes = {"Acelerante": 0.02, "Retardante": 0.015, "Plastificante": 0.01, "Para juntas frías": 0.012}
    if aditivo in porcentajes:
        vol_aditivo_L = cem_total * porcentajes[aditivo]

    # Cálculo de costos dinámico usando el diccionario 'precios'
    costo_total = (cem_total * (precios['cemento_kg'])) + \
                  (arena_total * precios['arena_m3']) + \
                  (trit_total * precios['trit_m3']) + \
                  (vol_aditivo_L * precios['aditivo_l'])

    # Formateo a 5 decimales para alta precisión en volúmenes pequeños
    def fmt(v): return f"{v:.5f}"

    if recipiente != "Unidades Estándar (m³, Litros, Bultos)":
        vol_r = int(recipiente.split(" ")[0])
        res = {
            "Cemento": f"{fmt(cem_total/50)} Bultos",
            "Arena": f"{fmt((arena_total*1000)/vol_r)} Baldes",
            "Triturado": f"{fmt((trit_total*1000)/vol_r)} Baldes",
            "Agua": f"{fmt(agua_total/vol_r)} Baldes",
            "Aditivo": f"{fmt(vol_aditivo_L)} L"
        }
    else:
        res = {
            "Cemento": f"{fmt(cem_total/50)} Bultos",
            "Arena": f"{fmt(arena_total)} m³",
            "Triturado": f"{fmt(trit_total)} m³",
            "Agua": f"{fmt(agua_total)} L",
            "Aditivo": f"{fmt(vol_aditivo_L)} L"
        }
    
    return res, costo_total

# --- INTERFAZ ---
st.title("Calculadora de Concreto NSR-10")

# --- NUEVA SECCIÓN: GESTIÓN DE PRECIOS (OPCIONAL) ---
with st.expander("⚙️ Configuración de Precios Unitarios (Opcional)"):
    st.write("Ajuste los precios para obtener un cálculo de costos exacto.")
    colp1, colp2, colp3 = st.columns(3)
    p_arena = colp1.number_input("Precio Arena (m³)", value=45000)
    p_trit = colp2.number_input("Precio Triturado (m³)", value=50000)
    p_aditivo = colp3.number_input("Precio Aditivo (Litro)", value=12000)
    
    st.write("**Precios de Cemento por Marca (Bulto 50kg):**")
    colp4, colp5, colp6, colp7 = st.columns(4)
    p_argos = colp4.number_input("Argos", value=32000)
    p_cemex = colp5.number_input("Cemex", value=31000)
    p_holcim = colp6.number_input("Holcim", value=32500)
    p_sika = colp7.number_input("Sika", value=34000)

# Mapeo de precios de cemento seleccionado
precios_cemento = {"Cementos Argos": p_argos, "Cemex": p_cemex, "Holcim": p_holcim, "Sika": p_sika}

tab_config, tab_resultados = st.tabs(["Configuración", "Resultados"])

with tab_config:
    col1, col2 = st.columns(2)
    with col1:
        resistencia = st.selectbox("Resistencia:", ["2500 PSI", "3000 PSI", "4000 PSI"])
        # Incrementamos precisión de entrada a 5 decimales
        volumen = st.number_input("Volumen:", min_value=0.00001, value=1.0, format="%.5f")
        unidades = st.selectbox("Unidades:", ["Metros Cúbicos (m³)", "Litros (L)"])
    
    with col2:
        marca_cem = st.selectbox("Marca Cemento:", ["Cementos Argos", "Cemex", "Holcim", "Sika"])
        marca_adi = st.selectbox("Marca Aditivo:", ["HOLCIM", "SIKA", "CEMEX", "ARGOS"])
        aditivo_tipo = st.selectbox("Tipo Aditivo:", ["Ninguno", "Acelerante", "Retardante", "Plastificante", "Para juntas frías"])
        recipiente = st.selectbox("Medición:", ["Unidades Estándar (m³, Litros, Bultos)", "19 Litros (Cuñete)", "12 Litros (Balde)"])

    # Ubicación usando el módulo externo
    st.markdown("---")
    dep = st.selectbox("Departamento:", list(lugares_colombia.keys()))
    mun = st.selectbox("Municipio:", lugares_colombia[dep])

# Diccionario de precios finales para la función
precios_finales = {
    'cemento_kg': precios_cemento[marca_cem] / 50,
    'arena_m3': p_arena,
    'trit_m3': p_trit,
    'aditivo_l': p_aditivo
}

with tab_resultados:
    res, costo = calcular_mezcla(resistencia, volumen, unidades, marca_cem, aditivo_tipo, recipiente, precios_finales)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Cemento", res["Cemento"])
    c2.metric("Arena", res["Arena"])
    c3.metric("Triturado", res["Triturado"])
    
    st.success(f"### Costo Estimado Total: ${costo:,.2f} COP")
    st.info(f"Basado en Cemento {marca_cem} y Aditivo {marca_adi}")

    # Lógica de clima (idéntica a la anterior pero con los nuevos datos)
    if dep != "Seleccione..." and mun != "Seleccione...":
        t, p, ciudad = obtener_clima_por_ciudad(mun)
        if t:
            st.write(f"☀️ Clima en {ciudad}: {t}°C | Prob. Lluvia: {p}%")
            if p > 50: st.error("Se recomienda usar ACELERANTE debido a riesgo de lluvia.")
