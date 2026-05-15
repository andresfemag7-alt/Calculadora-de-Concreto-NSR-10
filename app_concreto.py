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
    
    # Conversión a m3 para estandarizar el cálculo
    volumen_m3 = volumen / 1000 if unidades == "Litros (L)" else volumen

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

    # Desglose por recipientes (aquí entra el nuevo balde de 9L)
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
        unidades = st.selectbox("Unidades de volumen:", ["Metros Cúbicos (m³)", "Litros (L)"])
    with col_der:
        marca_cem = st.selectbox("Marca de Cemento:", ["Cementos Argos", "Cemex", "Holcim", "Sika"])
        marca_adi = st.selectbox("Marca del Aditivo:", ["Argos", "Cemex", "Holcim", "Sika"])
        tipo_adi = st.selectbox("Tipo de Aditivo:", ["Ninguno", "Acelerante", "Retardante", "Plastificante", "Para juntas frías"])
        
        # AGREGADO: Balde de 9 Litros
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
        p_cemento = st.number_input(f"Precio Bulto Cemento ({marca_cem})", value=32000)
        p_arena = st.number_input("Precio Arena (m³)", value=45000)
    with c2:
        p_aditivo = st.number_input(f"Precio Litro Aditivo ({marca_adi})", value=12000 if tipo_adi != "Ninguno" else 0)
        p_tritutado = st.number_input("Precio Triturado (m³)", value=55000)

with tab_resultados:
    st.subheader("Dosificación Resultante")
    
    # Cálculo final
    res, costo_est = calcular_mezcla(resistencia, volumen, unidades, p_cemento, p_arena, p_tritutado, p_aditivo, recipiente)
    
    col_mat1, col_mat2, col_mat3 = st.columns(3)
    col_mat1.info(f"**Cemento ({marca_cem}):**\n{res['Cemento']}")
    col_mat1.info(f"**Agua:**\n{res['Agua']}")
    col_mat2.success(f"**Arena:**\n{res['Arena']}")
    col_mat2.success(f"**Aditivo ({marca_adi}):**\n{res['Aditivo']}")
    col_mat3.warning(f"**Triturado:**\n{res['Triturado']}")
    
    st.metric("Costo Estimado Total (COP)", f"${costo_est:,.2f}")

    # Diagnóstico Climático
    st.markdown("---")
    if departamento_seleccionado != "Seleccione..." and municipio_seleccionado != "Seleccione...":
        temp, prob, ciudad = obtener_clima_por_ciudad(municipio_seleccionado)
        
        if temp is not None:
            st.markdown(f"<h2 style='text-align: center;'>Estado del Tiempo en {ciudad}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; font-size: 20px;'>Temperatura ambiente: {temp} °C | Probabilidad de lluvia: {prob}%</p>", unsafe_allow_html=True)
            
            if prob > 50:
                st.markdown(f"""
                <div style="background-color: #FF0000; padding: 30px; border-radius: 15px; border: 4px solid #900C3F; text-align: center; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);">
                    <h2 style="color: white; margin: 0; font-weight: 900; letter-spacing: 1px;">PROTOCOLOS POR PROBABILIDAD DE LLUVIA</h2>
                    <p style="color: white; font-size: 19px; margin-top: 20px; font-weight: 700; line-height: 1.5;">
                        ¡Pilas con el agua! Un aumento imprevisto en la humedad nos cambia la relación agua/cemento y golpea directamente la resistencia f'c. 
                        Es clave usar un <b>aditivo acelerante</b> para que el concreto fragüe rápido y no se nos lave. 
                        Tengan los <b>plásticos</b> a la mano para cubrir el frente de vaciado ante cualquier llovizna.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            elif temp > 28:
                st.markdown(f"""
                <div style="background-color: #FF8C00; padding: 30px; border-radius: 15px; border: 4px solid #E67E22; text-align: center; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);">
                    <h2 style="color: white; margin: 0; font-weight: 900; letter-spacing: 1px;">ALERTA POR ALTA TEMPERATURA</h2>
                    <p style="color: white; font-size: 19px; margin-top: 20px; font-weight: 700; line-height: 1.5;">
                        El calor está fuerte y la evaporación rápida nos puede causar fisuras por contracción plástica. 
                        Para mantener la trabajabilidad, lo ideal es usar un <b>plastificante o retardante</b>. 
                        No olviden humedecer bien las formaletas y los agregados antes de arrancar para refrescar el vaciado.
                    </p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #2ECC71; padding: 30px; border-radius: 15px; border: 4px solid #27AE60; text-align: center; box-shadow: 0px 4px 15px rgba(0,0,0,0.3);">
                    <h2 style="color: white; margin: 0; font-weight: 900; letter-spacing: 1px;">CONDICIONES CLIMÁTICAS ÓPTIMAS</h2>
                    <p style="color: white; font-size: 19px; margin-top: 20px; font-weight: 700; line-height: 1.5;">
                        Tenemos un clima ideal para que el diseño de mezcla se comporte según lo planeado. 
                        No hace falta ningún aditivo extra por clima; enfóquense en asegurar un <b>buen vibrado</b> 
                        y un acabado pulido para que la estructura quede 1A.
                    </p>
                </div>
                """, unsafe_allow_html=True)
