import streamlit as st  # Importamos Streamlit para crear la interfaz web interactiva
import pandas as pd     # Importamos Pandas para organizar los datos de costos en tablas
import plotly.express as px  # Importamos Plotly para generar la gráfica de barras comparativa
import base64           # Importamos Base64 para convertir la imagen de fondo en código web
import requests         # Importamos Requests para conectarnos a internet y traer datos del clima
from ubicaciones import lugares_colombia # Importamos el diccionario desde tu otro archivo .py

"""
Función del programa: APLICACIÓN WEB PARA DISEÑO DE MEZCLAS DE CONCRETO
Nombre del script: app_concreto.py
Autor: Ing. Civiles Andrés Felipe Madroñero Garces & José Manuel Arboleda Carvajal.
"""

# Configuramos la página: título de pestaña y diseño ancho para aprovechar el espacio lateral
st.set_page_config(page_title="Calculadora NSR-10", layout="wide")

# Función para inyectar CSS y la imagen de fondo personalizada
def cargar_estilos_y_fondo():
    try:
        # Abrimos la imagen en modo binario para procesarla
        with open("fondo2.png", "rb") as image_file:
            # Convertimos la imagen a texto (base64) para que el navegador la pueda renderizar
            imagen_base64 = base64.b64encode(image_file.read()).decode()
            
        # Definimos reglas de diseño CSS para el fondo, botones y textos
        css = f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{imagen_base64});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        /* Estilizamos las cajas de entrada y pestañas con fondo blanco semitransparente */
        .stTabs, .stSelectbox, .stNumberInput {{
            background-color: rgba(255, 255, 255, 0.9) !important;
            padding: 10px;
            border-radius: 8px;
        }}
        /* Color azul profesional para los títulos principales */
        h1, h2, h3 {{
            color: #1F618D !important;
            text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
        }}
        </style>
        """
        # Inyectamos el código CSS anterior en la aplicación de Streamlit
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        # Si no se encuentra el archivo físico, mostramos un mensaje de advertencia
        st.warning("No se encontro el archivo de fondo de pantalla.")

# Ejecutamos la carga de estilos al iniciar la app
cargar_estilos_y_fondo()

# Función para consultar el clima en tiempo real usando la API Open-Meteo
def obtener_clima_por_ciudad(municipio):
    try:
        # Definimos los parámetros de búsqueda para obtener Latitud y Longitud del municipio
        params_geo = {"name": municipio, "count": 1, "language": "es"}
        url_geo = "https://geocoding-api.open-meteo.com/v1/search"
        # Realizamos la petición HTTP a la API de geolocalización
        respuesta_geo = requests.get(url_geo, params=params_geo).json()
        
        # Validamos si la API devolvió resultados para evitar errores de ejecución
        if "results" not in respuesta_geo or not respuesta_geo["results"]:
            return None, None, "Ciudad no encontrada."

        # Extraemos coordenadas y nombre oficial detectado
        lat = respuesta_geo["results"][0]["latitude"]
        lon = respuesta_geo["results"][0]["longitude"]
        ciudad_detectada = respuesta_geo["results"][0]["name"]

        # Configuramos la petición para obtener temperatura y probabilidad de lluvia
        params_clima = {
            "latitude": lat, "longitude": lon,
            "daily": "precipitation_probability_max",
            "current_weather": "true", "timezone": "America/Bogota"
        }
        url_clima = "https://api.open-meteo.com/v1/forecast"
        # Realizamos la petición de los datos meteorológicos
        datos = requests.get(url_clima, params=params_clima).json()
        
        # Guardamos la temperatura y lluvia en variables
        temp = datos['current_weather']['temperature']
        prob_lluvia = datos['daily']['precipitation_probability_max'][0]
        
        return temp, prob_lluvia, ciudad_detectada
    except Exception as e:
        # Si falla el internet o la API, capturamos el error para no cerrar la app
        return None, None, f"Error de conexión: {e}"

# Función de cálculo de ingeniería para dosificación y análisis económico
def calcular_mezcla(resistencia, volumen, unidades, p_cem, p_are, p_tri, p_adi, recipiente):
    
    # Convertimos volumen a metros cúbicos (m3) para estandarizar todas las fórmulas técnicas
    volumen_m3 = volumen / 1000 if unidades == "Litros (L)" else volumen

    # Definimos la dosificación por cada m3 según la resistencia PSI seleccionada
    if resistencia == "2500 PSI":
        cem_kg, arena_m3, trit_m3, agua_l = 300 * volumen_m3, 0.50 * volumen_m3, 0.70 * volumen_m3, 170 * volumen_m3
    elif resistencia == "3000 PSI":
        cem_kg, arena_m3, trit_m3, agua_l = 350 * volumen_m3, 0.45 * volumen_m3, 0.70 * volumen_m3, 180 * volumen_m3
    else: 
        cem_kg, arena_m3, trit_m3, agua_l = 420 * volumen_m3, 0.40 * volumen_m3, 0.70 * volumen_m3, 200 * volumen_m3

    # Calculamos volumen de aditivo basándonos en un 1.5% del peso del cemento
    vol_aditivo_L = (cem_kg * 0.015) if p_adi > 0 else 0 

    # Sumamos los costos unitarios multiplicados por las cantidades calculadas
    costo_total = ( (cem_kg/50) * p_cem) + (arena_m3 * p_are) + (trit_m3 * p_tri) + (vol_aditivo_L * p_adi)

    # Sub-función para formatear números a 5 decimales (evita el error de mostrar 0.0 en volúmenes pequeños)
    def formatear_numero(valor):
        if valor == 0: return "0"
        return f"{valor:.5f}" 

    # Lógica para desglose según recipientes de obra si no se eligieron unidades estándar
    if recipiente != "Unidades Estándar (m³, Litros, Bultos)":
        vol_recipiente = int(recipiente.split(" ")[0]) 
        bultos_cemento = cem_kg / 50 
        baldes_arena = (arena_m3 * 1000) / vol_recipiente
        baldes_trit = (trit_m3 * 1000) / vol_recipiente
        baldes_agua = agua_l / vol_recipiente
        nombre_unidad = "cuñetes" if "Cuñete" in recipiente else "baldes"
            
        # Diccionario con textos de resultados para herramientas de medida
        resultados_texto = {
            "Cemento": f"{formatear_numero(bultos_cemento)} Bultos",
            "Arena": f"{formatear_numero(baldes_arena)} {nombre_unidad}",
            "Triturado": f"{formatear_numero(baldes_trit)} {nombre_unidad}",
            "Agua": f"{formatear_numero(baldes_agua)} {nombre_unidad}",
            "Aditivo": f"{formatear_numero(vol_aditivo_L)} L" if vol_aditivo_L > 0 else "No aplica"
        }
    else:
        # Diccionario con textos de resultados para medidas de ingeniería (m3 y L)
        resultados_texto = {
            "Cemento": f"{formatear_numero(cem_kg / 50)} Bultos",
            "Arena": f"{formatear_numero(arena_m3)} m³",
            "Triturado": f"{formatear_numero(trit_m3)} m³",
            "Agua": f"{formatear_numero(agua_l)} L",
            "Aditivo": f"{formatear_numero(vol_aditivo_L)} L" if vol_aditivo_L > 0 else "No aplica"
        }

    return resultados_texto, costo_total

# --- INTERFAZ WEB (FRONTEND) ---
st.title("Calculadora de Concreto NSR-10")
st.markdown("Plataforma técnica para el diseño de mezclas y dosificación en obra.")

# Creamos 3 pestañas para organizar el flujo del usuario: Parámetros, Precios y Resultados
tab_config, tab_precios, tab_resultados = st.tabs(["Configuración", "Precios de Materiales", "Resultados"])

# PESTAÑA 1: Captura de datos técnicos iniciales
with tab_config:
    st.subheader("Parámetros de Diseño")
    col_izq, col_der = st.columns(2)
    with col_izq:
        resistencia = st.selectbox("Resistencia a la compresión:", ["2500 PSI", "3000 PSI", "4000 PSI"])
        # Entrada de volumen con precisión de 5 decimales (formato %.5f) para evitar aproximaciones a cero
        volumen = st.number_input("Volumen requerido:", min_value=0.00001, value=1.0, step=0.00001, format="%.5f")
        unidades = st.selectbox("Unidades de volumen:", ["Metros Cúbicos (m³)", "Litros (L)"])
    with col_der:
        marca_cem = st.selectbox("Marca de Cemento:", ["Cementos Argos", "Cemex", "Holcim", "Sika"])
        marca_adi = st.selectbox("Marca del Aditivo:", ["Argos", "Cemex", "Holcim", "Sika"])
        tipo_adi = st.selectbox("Tipo de Aditivo:", ["Ninguno", "Acelerante", "Retardante", "Plastificante", "Para juntas frías"])
        recipiente = st.selectbox("Medición en obra:", [
            "Unidades Estándar (m³, Litros, Bultos)", "19 Litros (Cuñete)", 
            "12 Litros (Balde grande)", "10 Litros (Balde mediano)"
        ])
        
    st.markdown("---")
    st.subheader("Ubicación de la Obra")
    col_dep, col_mun = st.columns(2)
    with col_dep:
        # Obtenemos los departamentos cargando las llaves del diccionario de ubicaciones.py
        departamento_seleccionado = st.selectbox("Departamento:", list(lugares_colombia.keys()))
    with col_mun:
        # Filtramos los municipios según el departamento seleccionado previamente
        municipios_disponibles = lugares_colombia[departamento_seleccionado]
        municipio_seleccionado = st.selectbox("Municipio:", municipios_disponibles)

# PESTAÑA 2: Gestión dinámica de precios de mercado
with tab_precios:
    st.subheader("Ajuste de Precios Unitarios")
    st.info("Ajuste los precios según el mercado local o factura de proveedor.")
    c1, c2 = st.columns(2)
    with c1:
        # Permitimos editar el precio por bulto y m3 para cálculos de costos personalizados
        p_cemento = st.number_input(f"Precio Bulto Cemento ({marca_cem})", value=32000)
        p_arena = st.number_input("Precio Arena (m³)", value=45000)
    with c2:
        # El precio del aditivo se activa solo si se seleccionó uno en la pestaña anterior
        p_aditivo = st.number_input(f"Precio Litro Aditivo ({marca_adi})", value=12000 if tipo_adi != "Ninguno" else 0)
        p_tritutado = st.number_input("Precio Triturado (m³)", value=55000)

# PESTAÑA 3: Visualización de resultados técnicos y diagnóstico ambiental
with tab_resultados:
    st.subheader("Dosificación Resultante")
    
    # Invocamos la función de cálculo enviando todos los datos recolectados
    res, costo_est = calcular_mezcla(resistencia, volumen, unidades, p_cemento, p_arena, p_tritutado, p_aditivo, recipiente)
    
    # Organizamos los resultados finales en 3 columnas informativas
    col_mat1, col_mat2, col_mat3 = st.columns(3)
    col_mat1.info(f"**Cemento ({marca_cem}):**\n{res['Cemento']}")
    col_mat1.info(f"**Agua:**\n{res['Agua']}")
    col_mat2.success(f"**Arena:**\n{res['Arena']}")
    col_mat2.success(f"**Aditivo ({marca_adi}):**\n{res['Aditivo']}")
    col_mat3.warning(f"**Triturado:**\n{res['Triturado']}")
    
    # Mostramos el costo final de la mezcla con formato de moneda
    st.metric("Costo Estimado Total (COP)", f"${costo_est:,.2f}")

    st.markdown("---")
   # --- BLOQUE DE DIAGNÓSTICO CLIMÁTICO CORREGIDO Y ESTILIZADO ---
    if departamento_seleccionado != "Seleccione..." and municipio_seleccionado != "Seleccione...":
        # Traemos datos del clima para el municipio seleccionado
        temp, prob, ciudad = obtener_clima_por_ciudad(municipio_seleccionado)
        
        if temp is not None:
            # Título del clima centrado
            st.markdown(f"<h2 style='text-align: center;'>Clima en {ciudad}</h2>", unsafe_allow_html=True)
            # Info de temp y lluvia centrada
            st.markdown(f"<p style='text-align: center; font-size: 20px;'>Temperatura: {temp} °C | Probabilidad de Lluvia: {prob}%</p>", unsafe_allow_html=True)
            
            # --- LÓGICA DE ALERTAS CON COLORES VIVOS Y CENTRADOS ---
            if prob > 50:
                # Recuadro Rojo Vivo para Lluvia
                st.markdown(f"""
                <div style="background-color: #FF0000; padding: 25px; border-radius: 10px; border: 3px solid #900C3F; text-align: center;">
                    <h2 style="color: white; margin: 0; font-weight: 900;">ALERTA DE LLUVIA</h2>
                    <p style="color: white; font-size: 18px; margin-top: 15px; font-weight: 700;">
                        Recomendación: Se recomienda el uso de aditivo ACELERANTE para reducir el tiempo de fraguado y evitar el deslave; 
                        asimismo, es imperativo el empleo de plásticos protectores para evitar el contacto directo del agua de lluvia con la mezcla fresca.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            elif temp > 28:
                # Recuadro Naranja Vivo para Calor
                st.markdown(f"""
                <div style="background-color: #FF8C00; padding: 25px; border-radius: 10px; border: 3px solid #E67E22; text-align: center;">
                    <h2 style="color: white; margin: 0; font-weight: 900;">ALERTA DE CALOR</h2>
                    <p style="color: white; font-size: 18px; margin-top: 15px; font-weight: 700;">
                        Recomendación: Se recomienda aditivo PLASTIFICANTE/RETARDANTE para evitar fisuras por evaporación rápida del agua de curado.
                    </p>
                </div>
                """, unsafe_allow_html=True)

            else:
                # Recuadro Verde Vivo para Condiciones Óptimas
                st.markdown(f"""
                <div style="background-color: #2ECC71; padding: 25px; border-radius: 10px; border: 3px solid #27AE60; text-align: center;">
                    <h2 style="color: white; margin: 0; font-weight: 900;">CONDICIONES ÓPTIMAS</h2>
                    <p style="color: white; font-size: 18px; margin-top: 15px; font-weight: 700;">
                        No se requiere el uso de aditivos climáticos adicionales. Proceda con el vaciado estándar.
                    </p>
                </div>
                """, unsafe_allow_html=True)
