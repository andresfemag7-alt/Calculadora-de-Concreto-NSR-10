import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import requests

"""
Función del programa: APLICACIÓN WEB PARA DISEÑO DE MEZCLAS DE CONCRETO
Nombre del script: app_concreto.py
Autor: Ing. Civiles Andrés Felipe Madroñero Garces & José Manuel Arboleda Carvajal.
"""

st.set_page_config(page_title="Calculadora NSR-10", layout="wide")

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
        st.warning("No se encontro el archivo de fondo de pantalla.")

cargar_estilos_y_fondo()

# --- LÓGICA DE LUGARES EN COLOMBIA ---
lugares_colombia = {
    "Seleccione...": ["Seleccione un departamento primero"],
    "Antioquia": ["Seleccione...", "Medellín", "Bello", "Itagüí", "Envigado", "Rionegro"],
    "Bogotá D.C.": ["Seleccione...", "Bogotá"],
    "Cundinamarca": ["Seleccione...", "Soacha", "Chía", "Zipaquirá", "Cajicá"],
    "Quindío": ["Seleccione...", "Armenia", "Calarcá", "Montenegro", "Quimbaya", "La Tebaida"],
    "Risaralda": ["Seleccione...", "Pereira", "Dosquebradas", "Santa Rosa de Cabal"],
    "Valle del Cauca": ["Seleccione...", "Cali", "Palmira", "Buenaventura", "Buga", "Tuluá"]
}

def obtener_clima_por_ciudad(municipio):
    try:
        params_geo = {
            "name": municipio,
            "count": 1,
            "language": "es"
        }
        url_geo = "https://geocoding-api.open-meteo.com/v1/search"
        respuesta_geo = requests.get(url_geo, params=params_geo).json()
        
        if "results" not in respuesta_geo or not respuesta_geo["results"]:
            return None, None, "Ciudad no encontrada."

        lat = respuesta_geo["results"][0]["latitude"]
        lon = respuesta_geo["results"][0]["longitude"]
        ciudad_detectada = respuesta_geo["results"][0]["name"]

        params_clima = {
            "latitude": lat,
            "longitude": lon,
            "daily": "precipitation_probability_max",
            "current_weather": "true",
            "timezone": "America/Bogota"
        }
        url_clima = "https://api.open-meteo.com/v1/forecast"
        datos = requests.get(url_clima, params=params_clima).json()
        
        temp = datos['current_weather']['temperature']
        prob_lluvia = datos['daily']['precipitation_probability_max'][0]
        
        return temp, prob_lluvia, ciudad_detectada
    except Exception as e:
        return None, None, f"Error de conexión: {e}"

# --- LÓGICA MATEMÁTICA CORREGIDA ---
def calcular_mezcla(resistencia, volumen, unidades, marca, aditivo, recipiente):
    
    # 1. Corrección de unidades a Litros para evitar números microscópicos
    if unidades == "Litros (L)":
        volumen_m3 = volumen / 1000
    else:
        volumen_m3 = volumen

    # 2. Dosificación base en m3
    if resistencia == "2500 PSI":
        cem_kg = 300 * volumen_m3
        arena_m3 = 0.50 * volumen_m3
        trit_m3 = 0.70 * volumen_m3
        agua_l = 170 * volumen_m3
    elif resistencia == "3000 PSI":
        cem_kg = 350 * volumen_m3
        arena_m3 = 0.45 * volumen_m3
        trit_m3 = 0.70 * volumen_m3
        agua_l = 180 * volumen_m3
    else: 
        cem_kg = 420 * volumen_m3
        arena_m3 = 0.40 * volumen_m3
        trit_m3 = 0.70 * volumen_m3
        agua_l = 200 * volumen_m3

    # 3. Lógica de aditivos
    vol_aditivo_L = 0
    if aditivo == "Acelerante":
        vol_aditivo_L = (cem_kg * 0.02)
    elif aditivo == "Retardante":
        vol_aditivo_L = (cem_kg * 0.015) 
    elif aditivo == "Plastificante":
        vol_aditivo_L = (cem_kg * 0.01)
    elif aditivo == "Para juntas frías":
        vol_aditivo_L = (cem_kg * 0.012)

    # 4. Cálculo de costos
    costo_argos = (cem_kg * 600) + (arena_m3 * 40000) + (trit_m3 * 45000)
    costo_cemex = (cem_kg * 580) + (arena_m3 * 38000) + (trit_m3 * 42000)
    costo_holcim = (cem_kg * 610) + (arena_m3 * 42000) + (trit_m3 * 46000)

    # 5. Función de formateo dinámico (Evita que valores pequeños se muestren como 0.0)
    def formatear_numero(valor):
        if valor == 0:
            return "0"
        elif valor > 0 and valor < 0.1:
            return f"{valor:.3f}" # Muestra 3 decimales si es muy pequeño
        else:
            return f"{valor:.1f}" # Muestra 1 decimal para valores normales

    # 6. Distribución en recipientes
    if recipiente != "Unidades Estándar (m³, Litros, Bultos)":
        vol_recipiente = int(recipiente.split(" ")[0]) 
        bultos_cemento = cem_kg / 50 
        baldes_arena = (arena_m3 * 1000) / vol_recipiente
        baldes_trit = (trit_m3 * 1000) / vol_recipiente
        baldes_agua = agua_l / vol_recipiente
        
        if "Cuñete" in recipiente:
            nombre_unidad = "cuñetes"
        else:
            nombre_unidad = "baldes"
            
        resultados_texto = {
            "Cemento": f"{formatear_numero(bultos_cemento)} Bultos (50kg) - {marca}",
            "Arena": f"{formatear_numero(baldes_arena)} {nombre_unidad}",
            "Triturado": f"{formatear_numero(baldes_trit)} {nombre_unidad}",
            "Agua": f"{formatear_numero(baldes_agua)} {nombre_unidad}",
            "Aditivo": f"{formatear_numero(vol_aditivo_L)} Litros" if vol_aditivo_L > 0 else "No aplica"
        }
    else:
        resultados_texto = {
            "Cemento": f"{formatear_numero(cem_kg / 50)} Bultos (50kg) - {marca}",
            "Arena": f"{formatear_numero(arena_m3)} m³",
            "Triturado": f"{formatear_numero(trit_m3)} m³",
            "Agua": f"{formatear_numero(agua_l)} Litros",
            "Aditivo": f"{formatear_numero(vol_aditivo_L)} Litros" if vol_aditivo_L > 0 else "No aplica"
        }

    return resultados_texto, costo_argos, costo_cemex, costo_holcim

# --- INTERFAZ WEB (FRONTEND) ---
st.title("Calculadora de Concreto NSR-10")
st.markdown("Plataforma técnica para el diseño de mezclas y dosificación en obra.")

tab_config, tab_resultados = st.tabs(["Configuración de la Mezcla", "Resultados y Costos"])

with tab_config:
    st.subheader("Parámetros de Diseño")
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        resistencia = st.selectbox("Resistencia a la compresión:", ["2500 PSI", "3000 PSI", "4000 PSI"])
        volumen = st.number_input("Volumen requerido:", min_value=0.01, value=1.0, step=0.1)
        # Cambio de cm3 a Litros para mayor coherencia en construcción
        unidades = st.selectbox("Unidades de volumen:", ["Metros Cúbicos (m³)", "Litros (L)"])
    
    with col_der:
        marca = st.selectbox("Marca Comercial de Cemento:", ["Cementos Argos", "Cemex", "Holcim"])
        aditivo = st.selectbox("Aditivo Químico (Opcional):", ["Ninguno", "Acelerante", "Retardante", "Plastificante", "Para juntas frías"])
        recipiente = st.selectbox("Medición en obra (Contenedores):", [
            "Unidades Estándar (m³, Litros, Bultos)",
            "19 Litros (Cuñete de pintura)",
            "12 Litros (Balde negro grande)",
            "10 Litros (Balde negro mediano)",
            "9 Litros (Balde de construcción)",
            "8 Litros (Balde pequeño)"
        ])
        
    st.markdown("---")
    st.subheader("Ubicación de la Obra (Opcional para Diagnóstico de Clima)")
    col_dep, col_mun = st.columns(2)
    with col_dep:
        departamento_seleccionado = st.selectbox("Departamento:", list(lugares_colombia.keys()))
    with col_mun:
        municipios_disponibles = lugares_colombia[departamento_seleccionado]
        municipio_seleccionado = st.selectbox("Municipio:", municipios_disponibles)

with tab_resultados:
    st.subheader("Cantidades de Material Requeridas")
    resultados, c_argos, c_cemex, c_holcim = calcular_mezcla(resistencia, volumen, unidades, marca, aditivo, recipiente)
    
    col_mat1, col_mat2, col_mat3 = st.columns(3)
    col_mat1.info(f"**Cemento:**\n{resultados['Cemento']}")
    col_mat1.info(f"**Agua:**\n{resultados['Agua']}")
    col_mat2.success(f"**Arena:**\n{resultados['Arena']}")
    col_mat2.success(f"**Aditivo:**\n{resultados['Aditivo']}")
    col_mat3.warning(f"**Triturado:**\n{resultados['Triturado']}")
    
    st.markdown("---")
    st.subheader("Análisis de Costos Comparativos")
    
    datos_precios = pd.DataFrame({
        "Marca": ["Argos", "Cemex", "Holcim"],
        "Costo Total (COP)": [c_argos, c_cemex, c_holcim]
    })
    
    fig = px.bar(datos_precios, x="Marca", y="Costo Total (COP)", 
                 text="Costo Total (COP)", 
                 color="Marca",
                 color_discrete_sequence=["#1ABC9C", "#3498DB", "#E74C3C"],
                 title="Costo de la mezcla por marca comercial")
    
    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide', plot_bgcolor="rgba(255,255,255,0.8)")
    
    st.plotly_chart(fig, use_container_width=True)

    # =========================================================
    # DIAGNÓSTICO DEL CLIMA CONDICIONAL
    # =========================================================
    st.markdown("---")
    st.subheader("Diagnóstico de Campo en Tiempo Real")
    
    if departamento_seleccionado != "Seleccione..." and municipio_seleccionado != "Seleccione...":
        
        temp_actual, prob_lluvia, ciudad_actual = obtener_clima_por_ciudad(municipio_seleccionado)
        
        if temp_actual is not None:
            st.markdown(f"**Ubicación de obra:** {municipio_seleccionado}, {departamento_seleccionado} | **Temperatura actual:** {temp_actual} °C | **Probabilidad de precipitación:** {prob_lluvia}%")
            
            if prob_lluvia > 50:
                st.error("### **ALERTA CRÍTICA: Alta probabilidad de lluvia detectada para la jornada de hoy.**")
                
                if prob_lluvia == 100:
                    st.markdown("**AVISO:** La probabilidad es del 100%. Lluvia inminente o precipitación en curso en su ubicación.")
                    
                st.markdown("""
                **Recomendación Técnica:** Se sugiere modificar el diseño incorporando un aditivo **Acelerante**. 
                Este químico disminuye el tiempo de fraguado inicial, reduciendo drásticamente la vulnerabilidad de la mezcla fresca ante el deslave por lluvia. 
                Asegúrese de contar con recubrimientos plásticos en la obra.
                """)
                
            elif temp_actual > 28:
                st.warning("### **ALERTA PREVENTIVA: Temperaturas elevadas detectadas en la zona.**")
                st.markdown("""
                **Recomendación Técnica:** Se sugiere evaluar el uso de un aditivo **Plastificante** o **Retardante**. 
                El calor acelera la pérdida de humedad y el fraguado prematuro, lo cual puede generar fisuras por contracción. 
                Estos aditivos le permitirán mantener la manejabilidad del concreto sin alterar la relación agua/cemento.
                """)
                
            else:
                st.success("### **Condiciones climáticas óptimas para el vaciado de concreto estructural.**")
                st.markdown("""
                **Recomendación Técnica:** Mantenga los protocolos estándar estipulados en la NSR-10. 
                No se requiere adición de químicos por factores climáticos. Proceda con el curado con agua convencional.
                """)
        else:
            st.warning("No se pudo establecer conexión con el servidor meteorológico en este momento. Verifique las condiciones manualmente.")
    
    else:
        st.info("Para recibir un diagnóstico climático y recomendaciones de aditivos en tiempo real, por favor seleccione el **Departamento** y **Municipio** de la obra en la pestaña de configuración.")
