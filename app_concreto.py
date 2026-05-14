import streamlit as st
import pandas as pd
import plotly.express as px
import base64

"""
Función del programa: APLICACIÓN WEB PARA DISEÑO DE MEZCLAS DE CONCRETO (UI MEJORADA)
Nombre del script: app_concreto.py
Autor: Andrés Felipe Madroñero Garces IC.
"""

# Configuración inicial de la página web
st.set_page_config(page_title="Calculadora NSR-10", layout="wide")

# --- FUNCIÓN DE INYECCIÓN DE CSS (FONDO Y COLORES) ---
def cargar_estilos_y_fondo():
    try:
        # Codificamos la imagen local a base64 para inyectarla en el CSS web
        with open("fondo1.png", "rb") as image_file:
            imagen_base64 = base64.b64encode(image_file.read()).decode()
            
        # Inyectamos el CSS personalizado
        css = f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{imagen_base64});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        /* Fondo blanco semitransparente para los bloques principales */
        .stTabs, .stSelectbox, .stNumberInput {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            padding: 10px;
            border-radius: 8px;
        }}
        h1, h2, h3 {{
            color: #1F618D !important; /* Azul profesional */
            text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
        }}
        </style>
        """
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("No se encontró el archivo 'fondo.png' para el fondo de pantalla.")

cargar_estilos_y_fondo()

# --- LÓGICA MATEMÁTICA ---
def calcular_mezcla(resistencia, volumen, unidades, marca, aditivo, recipiente):
    if unidades == "Centímetros Cúbicos (cm³)":
        volumen = volumen / 1000000

    if resistencia == "2500 PSI":
        cem_kg, arena_m3, trit_m3, agua_l = 300 * volumen, 0.50 * volumen, 0.70 * volumen, 170 * volumen
    elif resistencia == "3000 PSI":
        cem_kg, arena_m3, trit_m3, agua_l = 350 * volumen, 0.45 * volumen, 0.70 * volumen, 180 * volumen
    else: 
        cem_kg, arena_m3, trit_m3, agua_l = 420 * volumen, 0.40 * volumen, 0.70 * volumen, 200 * volumen

    vol_aditivo_L = 0
    if aditivo == "Acelerante":
        vol_aditivo_L = (cem_kg * 0.02)
    elif aditivo == "Retardante":
        vol_aditivo_L = (cem_kg * 0.015) 
    elif aditivo == "Plastificante":
        vol_aditivo_L = (cem_kg * 0.01)
    elif aditivo == "Para juntas frías":
        vol_aditivo_L = (cem_kg * 0.012)

    costo_argos = (cem_kg * 600) + (arena_m3 * 40000) + (trit_m3 * 45000)
    costo_cemex = (cem_kg * 580) + (arena_m3 * 38000) + (trit_m3 * 42000)
    costo_holcim = (cem_kg * 610) + (arena_m3 * 42000) + (trit_m3 * 46000)

    if recipiente != "Unidades Estándar (m³, Litros, Bultos)":
        vol_recipiente = int(recipiente.split(" ")[0]) 
        bultos_cemento = cem_kg / 50 
        baldes_arena = (arena_m3 * 1000) / vol_recipiente
        baldes_trit = (trit_m3 * 1000) / vol_recipiente
        baldes_agua = agua_l / vol_recipiente
        
        resultados_texto = {
            "Cemento": f"{bultos_cemento:.1f} Bultos (50kg)",
            "Arena": f"{baldes_arena:.1f} baldes/cuñetes",
            "Triturado": f"{baldes_trit:.1f} baldes/cuñetes",
            "Agua": f"{baldes_agua:.1f} baldes/cuñetes",
            "Aditivo": f"{vol_aditivo_L:.2f} Litros" if vol_aditivo_L > 0 else "No aplica"
        }
    else:
        resultados_texto = {
            "Cemento": f"{(cem_kg / 50):.1f} Bultos (50kg)",
            "Arena": f"{arena_m3:.2f} m³",
            "Triturado": f"{trit_m3:.2f} m³",
            "Agua": f"{agua_l:.1f} Litros",
            "Aditivo": f"{vol_aditivo_L:.2f} Litros" if vol_aditivo_L > 0 else "No aplica"
        }

    return resultados_texto, costo_argos, costo_cemex, costo_holcim

# --- INTERFAZ WEB (FRONTEND) ---
st.title("Calculadora de Concreto NSR-10")
st.markdown("Plataforma técnica para el diseño de mezclas y dosificación en obra.")

# Organización mediante pestañas (Tabs) para un diseño limpio
tab_config, tab_resultados = st.tabs(["Configuración de la Mezcla", "Resultados y Costos"])

with tab_config:
    st.subheader("Parámetros de Diseño")
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        resistencia = st.selectbox("Resistencia a la compresión:", ["2500 PSI", "3000 PSI", "4000 PSI"])
        volumen = st.number_input("Volumen requerido:", min_value=0.01, value=1.0, step=0.1)
        unidades = st.selectbox("Unidades de volumen:", ["Metros Cúbicos (m³)", "Centímetros Cúbicos (cm³)"])
    
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

with tab_resultados:
    st.subheader("Cantidades de Material Requeridas")
    resultados, c_argos, c_cemex, c_holcim = calcular_mezcla(resistencia, volumen, unidades, marca, aditivo, recipiente)
    
    # Mostrar resultados en columnas para mayor claridad
    col_mat1, col_mat2, col_mat3 = st.columns(3)
    col_mat1.info(f"**Cemento:**\n{resultados['Cemento']}")
    col_mat1.info(f"**Agua:**\n{resultados['Agua']}")
    
    col_mat2.success(f"**Arena:**\n{resultados['Arena']}")
    col_mat2.success(f"**Aditivo:**\n{resultados['Aditivo']}")
    
    col_mat3.warning(f"**Triturado:**\n{resultados['Triturado']}")
    
    st.markdown("---")
    st.subheader("Análisis de Costos Comparativos")
    
    # Creación de gráfico interactivo y vivo usando Plotly
    datos_precios = pd.DataFrame({
        "Marca": ["Argos", "Cemex", "Holcim"],
        "Costo Total (COP)": [c_argos, c_cemex, c_holcim]
    })
    
    # Definición de una paleta de colores vivos
    fig = px.bar(datos_precios, x="Marca", y="Costo Total (COP)", 
                 text="Costo Total (COP)", 
                 color="Marca",
                 color_discrete_sequence=["#1ABC9C", "#3498DB", "#E74C3C"],
                 title="Costo de la mezcla por marca comercial")
    
    fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
    fig.update_layout(uniformtext_minsize=10, uniformtext_mode='hide', plot_bgcolor="rgba(255,255,255,0.8)")
    
    st.plotly_chart(fig, use_container_width=True)