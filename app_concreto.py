import streamlit as st  # Interfaz visual
import pandas as pd     # Manejo de datos
import plotly.express as px  # Gráficas
import base64           # Procesamiento de imagen de fondo
import requests         # Consulta de API de clima
from ubicaciones import lugares_colombia # Base de datos de municipios

"""
Función del programa: APLICACIÓN WEB PARA DISEÑO DE MEZCLAS DE CONCRETO
Autores: Ing. Civiles Andrés Felipe Madroñero Garces & José Manuel Arboleda Carvajal.
"""

# Configuración de pantalla ancha
st.set_page_config(page_title="Calculadora NSR-10", layout="wide")

# --- BASE DE DATOS DE ADITIVOS ---
# Base de datos definitiva: Precio único por unidad de litro (COP/L)
catalogo_precio_por_litro = {
    "SIKA": {
        "Acelerante": 34975,         # Basado en Sikaset-L (Garrafa de 5 kg)
        "Retardante": "Bajo cotización",
        "Plastificante": 32825,      # Basado en Plastocrete DM (Cuñete)
        "Para juntas frías": 243994  # Basado en Sikadur-32 Primer (Juego)
    },
    "TOXEMENT": {
        "Acelerante": 25989,         # Basado en Accelguard HE (Garrafa)
        "Retardante": "Bajo cotización",
        "Plastificante": "Bajo cotización",
        "Para juntas frías": 84656    # Basado en Epoxitoc (Galón)
    },
    "MASTER BUILDERS": {
        "Acelerante": "Bajo cotización",
        "Retardante": "Bajo cotización",
        "Plastificante": "Bajo cotización",
        "Para juntas frías": 195000  # Basado en MasterBrace ADH
    },
    "Genérico / Otras marcas": {
        "Acelerante": 0,
        "Retardante": 0,
        "Plastificante": 0,
        "Para juntas frías": 0
    }
}

# --- ESTILOS Y FONDO ---
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
        .stTabs, .stSelectbox, .stNumberInput {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            padding: 10px;
            border-radius: 8px;
        }}
        h1, h2, h3 {{
            color: #1F618D !important;
            text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("No se encontró el archivo de fondo de pantalla.")

cargar_estilos_y_fondo()

# --- FUNCIÓN DE CLIMA ---
def obtener_clima_por_ciudad(municipio):
    try:
        # Búsqueda de coordenadas
        params_geo = {"name": municipio, "count": 1, "language": "es"}
        url_geo = "https://geocoding-api.open-meteo.com/v1/search"
        respuesta_geo = requests.get(url_geo, params=params_geo).json()
        
        if "results" not in respuesta_geo or not respuesta_geo["results"]:
            return None, None, "Ciudad no encontrada."

        lat = respuesta_geo["results"][0]["latitude"]
        lon = respuesta_geo["results"][0]["longitude"]
        ciudad_detectada = respuesta_geo["results"][0]["name"]

        # Consulta de clima actual
        params_clima = {
            "latitude": lat, "longitude": lon,
            "daily": "precipitation_probability_max",
            "current_weather": "true", "timezone": "America/Bogota"
        }
        url_clima = "https://api.open-meteo.com/v1/forecast"
        datos = requests.get(url_clima, params=params_clima).json()
        
        temp = datos['current_weather']['temperature']
        prob_lluvia = datos['daily']['precipitation_probability_max'][0]
        
        return temp, prob_lluvia, ciudad_detectada
    except Exception as e:
        return None, None, f"Error: {e}"

# --- LÓGICA DE CÁLCULO (NSR-10) ---
def calcular_mezcla(resistencia, volumen, unidades, p_cem, p_are, p_tri, p_adi, recipiente):
    
    # Conversión a m3 para estandarizar el cálculo (Añadido cm3)
    if unidades == "Litros (L)":
        volumen_m3 = volumen / 1000
    elif unidades == "Centímetros Cúbicos (cm³)":
        volumen_m3 = volumen / 1000000
    else:
        volumen_m3 = volumen

    # Dosificación por m3
    if resistencia == "2500 PSI":
        cem_kg, arena_m3, trit_m3, agua_l = 300 * volumen_m3, 0.50 * volumen_m3, 0.70 * volumen_m3, 170 * volumen_m3
    elif resistencia == "3000 PSI":
        cem_kg, arena_m3, trit_m3, agua_l = 350 * volumen_m3, 0.45 * volumen_m3, 0.70 * volumen_m3, 180 * volumen_m3
    else: 
        cem_kg, arena_m3, trit_m3, agua_l = 420 * volumen_m3, 0.40 * volumen_m3, 0.70 * volumen_m3, 200 * volumen_m3

    # Aditivo basado en peso de cemento
    vol_aditivo_L = (cem_kg * 0.015) if p_adi > 0 else 0 

    # Costo total con precios dinámicos
    costo_total = ( (cem_kg/50) * p_cem) + (arena_m3 * p_are) + (trit_m3 * p_tri) + (vol_aditivo_L * p_adi)

    # Formateo a 5 decimales para evitar el error de aproximación a cero
    def formatear_numero(valor):
        if valor == 0: return "0"
        return f"{valor:.5f}" 

    # Desglose por recipientes (aquí entra el balde de 9L)
    if recipiente != "Unidades Estándar (m³, Litros, Bultos)":
        # Extrae el número (ej. "9") del string de la opción seleccionada
        vol_recipiente = int(recipiente.split(" ")[0]) 
        bultos_cemento = cem_kg / 50 
        baldes_arena = (arena_m3 * 1000) / vol_recipiente
        baldes_trit = (trit_m3 * 1000) / vol_recipiente
        baldes_agua = agua_l / vol_recipiente
        nombre_unidad = "cuñetes" if "Cuñete" in recipiente else "baldes"
            
        resultados_texto = {
            "Cemento": f"{formatear_numero(bultos_cemento)} Bultos",
            "Arena": f"{formatear_numero(baldes_arena)} {nombre_unidad}",
            "Triturado": f"{formatear_numero(baldes_trit)} {nombre_unidad}",
            "Agua": f"{formatear_numero(baldes_agua)} {nombre_unidad}",
            "Aditivo": f"{formatear_numero(vol_aditivo_L)} L" if vol_aditivo_L > 0 else "No aplica"
        }
    else:
        resultados_texto = {
            "Cemento": f"{formatear_numero(cem_kg / 50)} Bultos",
            "Arena": f"{formatear_numero(arena_m3)} m³",
            "Triturado": f"{formatear_numero(trit_m3)} m³",
            "Agua": f"{formatear_numero(agua_l)} L",
            "Aditivo": f"{formatear_numero(vol_aditivo_L)} L" if vol_aditivo_L > 0 else "No aplica"
        }

    return resultados_texto, costo_total

# --- INTERFAZ ---
st.title("Calculadora de Concreto NSR-10")
st.markdown("Plataforma técnica para el diseño de mezclas y dosificación en obra.")

tab_config, tab_precios, tab_resultados = st.tabs(["Configuración", "Precios de Materiales", "Resultados"])

with tab_config:
    st.subheader("Parámetros de Diseño")
    col_izq, col_der = st.columns(2)
    with col_izq:
        resistencia = st.selectbox("Resistencia a la compresión:", ["2500 PSI", "3000 PSI", "4000 PSI"])
        # Precisión de 5 decimales en el input
        volumen = st.number_input("Volumen requerido:", min_value=0.00001, value=1.0, step=0.00001, format="%.5f")
        # Se añade la unidad de Centímetros Cúbicos
        unidades = st.selectbox("Unidades de volumen:", ["Metros Cúbicos (m³)", "Litros (L)", "Centímetros Cúbicos (cm³)"])
    with col_der:
        # Se retira Sika de los cementos
        marca_cem = st.selectbox("Marca de Cemento:", ["Cementos Argos", "Cemex", "Holcim"])
        # Se vincula a las marcas de la base de datos oficial
        marca_adi = st.selectbox("Marca del Aditivo:", list(catalogo_precio_por_litro.keys()))
        tipo_adi = st.selectbox("Tipo de Aditivo:", ["Ninguno", "Acelerante", "Retardante", "Plastificante", "Para juntas frías"])
        
        recipiente = st.selectbox("Medición en obra:", [
            "Unidades Estándar (m³, Litros, Bultos)", 
            "19 Litros (Cuñete)", 
            "12 Litros (Balde grande)", 
            "10 Litros (Balde mediano)",
            "9 Litros (Balde)" 
        ])
        
    st.markdown("---")
    st.subheader("Ubicación de la Obra")
    col_dep, col_mun = st.columns(2)
    with col_dep:
        departamento_seleccionado = st.selectbox("Departamento:", list(lugares_colombia.keys()))
    with col_mun:
        municipios_disponibles = lugares_colombia[departamento_seleccionado]
        municipio_seleccionado = st.selectbox("Municipio:", municipios_disponibles)

with tab_precios:
    st.subheader("Ajuste de Precios Unitarios")
    c1, c2 = st.columns(2)
    with c1:
        # Lógica para precios base de cemento según fabricante
        if marca_cem
