# Importa Streamlit: librería para la interfaz visual.
import streamlit as st 
# Importa Pandas: manipulación de tablas de datos.
import pandas as pd 
# Importa Plotly Express: creación de gráficas interactivas.
import plotly.express as px 
# Importa Base64: codificación de imágenes para el fondo.
import base64 
# Importa Requests: peticiones web para consultar el clima.
import requests 
# Importa Socrata de sodapy: librería oficial para conectarse a Datos Abiertos Colombia.
from sodapy import Socrata 

# Configuración inicial: Nombre de la página y diseño ancho.
st.set_page_config(page_title="Diseño de Mezclas", layout="wide")

# ==========================================
# 1. DISEÑO UI (CSS SÓLIDO Y PROFESIONAL)
# ==========================================
# Función para inyectar diseño web (CSS) personalizado.
def cargar_estilos_y_fondo():
    try:
        # Abre la imagen de fondo en modo lectura binaria.
        with open("fondo2.png", "rb") as image_file:
            # Codifica la imagen para que el navegador web pueda leerla.
            imagen_base64 = base64.b64encode(image_file.read()).decode()
            
        # Variable que guarda código CSS puro para embellecer la interfaz.
        css = f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{imagen_base64});
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .stTabs, .stSelectbox, .stNumberInput {{
            background-color: rgba(245, 247, 250, 0.95) !important;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #2980B9;
            box-shadow: 0px 2px 10px rgba(0,0,0,0.1);
        }}
        html, body, p, div, span, label {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            font-weight: 600 !important;
            color: #1a252f;
        }}
        h1, h2, h3 {{
            color: #1A5276 !important; 
            font-weight: 800 !important;
            text-transform: uppercase;
        }}
        </style>
        """
        # Inyecta el código CSS en la aplicación.
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        pass # Ignora errores visuales si la imagen no existe.

# Ejecutamos la función de diseño.
cargar_estilos_y_fondo()

# ==========================================
# 2. BASE DE DATOS MEDIANTE LIBRERÍA OFICIAL (SODAPY)
# ==========================================
# @st.cache_data guarda la consulta en memoria RAM para no retrasar la aplicación.
@st.cache_data
def obtener_municipios_colombia():
    try:
        # Conecta con el portal de Datos Abiertos del gobierno usando la librería Socrata.
        # 'None' indica que el dataset es público y no requiere contraseña.
        cliente = Socrata("www.datos.gov.co", None)
        
        # Obtiene el dataset oficial de municipios (código 'xdk5-pm3f') limitando a 1200 resultados.
        resultados = cliente.get("xdk5-pm3f", limit=1200)
        
        # Convierte los resultados descargados en una tabla de Pandas.
        df = pd.DataFrame.from_records(resultados)
        
        # Agrupa la tabla por departamento y crea una lista de sus municipios.
        diccionario = df.groupby('departamento')['municipio'].apply(list).to_dict()
        return diccionario
    except Exception as e:
        # Diccionario de respaldo pequeño por si el servidor del gobierno cae.
        return {"Bogotá D.C.": ["Bogotá"], "Antioquia": ["Medellín"], "Valle del Cauca": ["Cali"]}

# Ejecuta la función limpia apoyada en la librería.
lugares_colombia = obtener_municipios_colombia()

# Extrae los departamentos y los ordena alfabéticamente.
lista_departamentos = sorted(list(lugares_colombia.keys()))
# Asegura que la instrucción "Seleccione..." esté al principio del menú.
if "Seleccione..." in lista_departamentos:
    lista_departamentos.remove("Seleccione...")
lista_departamentos.insert(0, "Seleccione...")

# Diccionario de precios promedio de Cemento por bulto.
precios_cemento = {
    "Argos": 33500, "Cemex": 32000, "Holcim": 34000, "Sika": 45000 
}

# Diccionario anidado de precios de Aditivos por Litro.
precios_aditivos = {
    "Argos": {"Acelerante": 8000, "Retardante": 7500, "Plastificante": 9000, "Para juntas frías": 11000},
    "Cemex": {"Acelerante": 7800, "Retardante": 7200, "Plastificante": 8800, "Para juntas frías": 10500},
    "Holcim": {"Acelerante": 8200, "Retardante": 7600, "Plastificante": 9200, "Para juntas frías": 11500},
    "Sika": {"Acelerante": 12000, "Retardante": 11000, "Plastificante": 13000, "Para juntas frías": 15000}
}

# Variable del costo del agua (precio nacional estimado).
precio_agua_litro = 3.5 
# Diccionario con los precios estimados de arena y triturado por departamento.
precios_regionales = {
    "Amazonas": {"arena": 85000, "trit": 90000}, "Antioquia": {"arena": 45000, "trit": 50000},
    "Arauca": {"arena": 60000, "trit": 65000}, "Atlántico": {"arena": 35000, "trit": 40000},
    "Bogotá D.C.": {"arena": 50000, "trit": 55000}, "Bolívar": {"arena": 38000, "trit": 42000},
    "Boyacá": {"arena": 42000, "trit": 48000}, "Caldas": {"arena": 45000, "trit": 49000},
    "Caquetá": {"arena": 65000, "trit": 70000}, "Casanare": {"arena": 55000, "trit": 60000},
    "Cauca": {"arena": 48000, "trit": 52000}, "Cesar": {"arena": 40000, "trit": 45000},
    "Chocó": {"arena": 75000, "trit": 80000}, "Córdoba": {"arena": 38000, "trit": 43000},
    "Cundinamarca": {"arena": 48000, "trit": 52000}, "Guainía": {"arena": 90000, "trit": 95000},
    "Guaviare": {"arena": 85000, "trit": 90000}, "Huila": {"arena": 45000, "trit": 49000},
    "La Guajira": {"arena": 42000, "trit": 47000}, "Magdalena": {"arena": 39000, "trit": 44000},
    "Meta": {"arena": 52000, "trit": 57000}, "Nariño": {"arena": 50000, "trit": 55000},
    "Norte de Santander": {"arena": 44000, "trit": 48000}, "Putumayo": {"arena": 70000, "trit": 75000},
    "Quindío": {"arena": 46000, "trit": 50000}, "Risaralda": {"arena": 45000, "trit": 49000},
    "San Andrés y Providencia": {"arena": 120000, "trit": 130000}, "Santander": {"arena": 44000, "trit": 48000},
    "Sucre": {"arena": 38000, "trit": 42000}, "Tolima": {"arena": 46000, "trit": 51000},
    "Valle del Cauca": {"arena": 45000, "trit": 49000}, "Vaupés": {"arena": 95000, "trit": 100000},
    "Vichada": {"arena": 85000, "trit": 90000}
}

# ==========================================
# 3. LÓGICA MATEMÁTICA Y DE COSTOS
# ==========================================
# Función para asegurar precisión decimal sin redondear a 0.
def formatear_numero(valor):
    if valor == 0: return "0" 
    if valor < 0.01: return f"{valor:.4f}" 
    if valor < 0.1: return f"{valor:.3f}"  
    return f"{valor:.2f}" 

# Función principal que realiza todos los cálculos de diseño.
def calcular_mezcla(resistencia, volumen, unidades, depto_seleccionado, marca_cem, marca_adi, tipo_adi, recipiente):
    # Conversión condicional: si entra en litros, divide por mil para operar en m3.
    volumen_m3 = volumen / 1000 if unidades == "Litros (L)" else volumen

    # Dosificación según la NSR-10.
    if resistencia == "2500 PSI":
        cem_kg, arena_m3, trit_m3, agua_l = 300 * volumen_m3, 0.50 * volumen_m3, 0.70 * volumen_m3, 170 * volumen_m3
    elif resistencia == "3000 PSI":
        cem_kg, arena_m3, trit_m3, agua_l = 350 * volumen_m3, 0.45 * volumen_m3, 0.70 * volumen_m3, 180 * volumen_m3
    else: 
        cem_kg, arena_m3, trit_m3, agua_l = 420 * volumen_m3, 0.40 * volumen_m3, 0.70 * volumen_m3, 200 * volumen_m3

    # Cálculo de litros de aditivo basado en el porcentaje del peso del cemento.
    vol_aditivo_L = 0
    if tipo_adi == "Acelerante": vol_aditivo_L = (cem_kg * 0.02)
    elif tipo_adi == "Retardante": vol_aditivo_L = (cem_kg * 0.015) 
    elif tipo_adi == "Plastificante": vol_aditivo_L = (cem_kg * 0.01)
    elif tipo_adi == "Para juntas frías": vol_aditivo_L = (cem_kg * 0.012)

    # Extrae el precio de agregados del departamento; si falla, usa Antioquia por defecto.
    precio_arena_m3 = precios_regionales.get(depto_seleccionado, {"arena": 45000})["arena"]
    precio_trit_m3 = precios_regionales.get(depto_seleccionado, {"trit": 50000})["trit"]

    costos_totales = {}
    # Bucle para evaluar los costos de las 4 marcas de cemento.
    for marca in precios_cemento.keys():
        bultos = cem_kg / 50 
        costo_cemento_total = bultos * precios_cemento[marca]
        costo_agregados = (arena_m3 * precio_arena_m3) + (trit_m3 * precio_trit_m3) + (agua_l * precio_agua_litro)
        
        costo_aditivo_total = 0
        if tipo_adi != "Ninguno":
            costo_aditivo_total = vol_aditivo_L * precios_aditivos[marca_adi][tipo_adi]
            
        costos_totales[marca] = costo_cemento_total + costo_agregados + costo_aditivo_total

    bultos_req = cem_kg / 50
    # Modificación de unidades a recipientes si aplica.
    if recipiente != "Unidades Estándar (m³, Litros, Bultos)":
        vol_recipiente = int(recipiente.split(" ")[0]) 
        baldes_arena, baldes_trit, baldes_agua = (arena_m3 * 1000) / vol_recipiente, (trit_m3 * 1000) / vol_recipiente, agua_l / vol_recipiente
        unidad_rec = "cuñetes" if "Cuñete" in recipiente else "baldes"
            
        resultados_texto = {
            "Cemento": f"{formatear_numero(bultos_req)} Bultos (50kg)",
            "Arena": f"{formatear_numero(baldes_arena)} {unidad_rec}",
            "Triturado": f"{formatear_numero(baldes_trit)} {unidad_rec}",
            "Agua": f"{formatear_numero(baldes_agua)} {unidad_rec}",
            "Aditivo": f"{formatear_numero(vol_aditivo_L)} L" if vol_aditivo_L > 0 else "N/A"
        }
    else:
        resultados_texto = {
            "Cemento": f"{formatear_numero(bultos_req)} Bultos",
            "Arena": f"{formatear_numero(arena_m3)} m³",
            "Triturado": f"{formatear_numero(trit_m3)} m³",
            "Agua": f"{formatear_numero(agua_l)} Litros",
            "Aditivo": f"{formatear_numero(vol_aditivo_L)} L" if vol_aditivo_L > 0 else "N/A"
        }

    return resultados_texto, costos_totales

# ==========================================
# 4. INTERFAZ WEB (FRONTEND)
# ==========================================
# Título sobrio y descriptivo
st.title("Diseño de Mezclas de Concreto")
st.markdown("Plataforma avanzada para el cálculo de materiales, análisis de costos regionales y diagnóstico climático.")

# Pestañas de navegación.
tab_config, tab_resultados = st.tabs(["Configuración de la Mezcla", "Resultados y Análisis"])

# Pestaña 1: Configuración.
with tab_config:
    st.subheader("Ubicación de la Obra")
    col_dep, col_mun = st.columns(2)
    with col_dep:
        departamento = st.selectbox("Departamento:", lista_departamentos)
    with col_mun:
        if departamento != "Seleccione...":
            # Si hay departamento, carga sus municipios consultados con la librería.
            municipio = st.selectbox("Municipio:", ["Seleccione..."] + sorted(lugares_colombia.get(departamento, [])))
        else:
            municipio = st.selectbox("Municipio:", ["Seleccione un departamento primero"])
            
    st.markdown("---")
    st.subheader("Parámetros Estructurales")
    col1, col2, col3 = st.columns(3)
    with col1:
        resistencia = st.selectbox("Resistencia (Compresión):", ["2500 PSI", "3000 PSI", "4000 PSI"])
    with col2:
        unidades = st.selectbox("Unidades de volumen:", ["Metros Cúbicos (m³)", "Litros (L)"])
    with col3:
        # Control numérico preciso.
        volumen = st.number_input("Volumen requerido:", min_value=0.001, value=1.0, step=0.1, format="%.4f")

    st.markdown("---")
    st.subheader("Especificaciones de Materiales")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        # Selector dinámico de precios.
        lista_marcas_cem = [f"{marca} (${precio:,.0f}/bulto)" for marca, precio in precios_cemento.items()]
        marca_cemento = st.selectbox("Marca de Cemento:", lista_marcas_cem)
        marca_pura_cem = marca_cemento.split(" ")[0] 
    with col_m2:
        marca_aditivo = st.selectbox("Marca del Aditivo:", ["Argos", "Cemex", "Holcim", "Sika"])
    with col_m3:
        tipo_aditivo = st.selectbox("Tipo de Aditivo:", ["Ninguno", "Acelerante", "Retardante", "Plastificante", "Para juntas frías"])
        
    # Herramienta de medición sin descripciones redundantes.
    recipiente = st.selectbox("Herramienta de Medición en Obra:", [
        "Unidades Estándar (m³, Litros, Bultos)", "19 Litros (Cuñete)",
        "12 Litros (Balde negro grande)", "10 Litros (Balde negro mediano)"
    ])

# Pestaña 2: Resultados.
with tab_resultados:
    st.subheader("Cantidades Matemáticas Exactas")
    
    # Valida que exista selección antes de procesar.
    if departamento == "Seleccione...":
        st.warning("Por favor seleccione un Departamento en la pestaña de Configuración para calcular los costos regionales.")
    else:
        resultados, costos = calcular_mezcla(resistencia, volumen, unidades, departamento, marca_pura_cem, marca_aditivo, tipo_aditivo, recipiente)
        
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.info(f"**CEMENTO**\n\n{resultados['Cemento']}")
        c2.success(f"**ARENA**\n\n{resultados['Arena']}")
        c3.warning(f"**TRITURADO**\n\n{resultados['Triturado']}")
        c4.info(f"**AGUA**\n\n{resultados['Agua']}")
        c5.error(f"**ADITIVO**\n\n{resultados['Aditivo']}")
        
        st.markdown("---")
        st.subheader(f"Comparativa de Costos (Precios promediados para {departamento})")
        
        # Preparación de datos para la gráfica.
        df_costos = pd.DataFrame({
            "Marca Estructural": list(costos.keys()),
            "Costo Total (COP)": list(costos.values())
        })
        
        # Generación del gráfico de barras interactivo.
        fig = px.bar(df_costos, x="Marca Estructural", y="Costo Total (COP)", 
                     text="Costo Total (COP)", color="Marca Estructural",
                     color_discrete_sequence=["#1ABC9C", "#3498DB", "#E74C3C", "#F1C40F"],
                     title="Costo final de la mezcla incluyendo agregados y aditivos")
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside', textfont=dict(size=14, color='black'))
        fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide', plot_bgcolor="rgba(255,255,255,0.8)")
        st.plotly_chart(fig, use_container_width=True)

        # ==========================================
        # DIAGNÓSTICO CLIMÁTICO
        # ==========================================
        st.markdown("---")
        if municipio != "Seleccione...":
            try: 
                # Petición a la API externa para validar clima actual.
                params_geo = {"name": municipio, "count": 1, "language": "es"}
                res_geo = requests.get("https://geocoding-api.open-meteo.com/v1/search", params=params_geo).json()
                lat, lon = res_geo["results"][0]["latitude"], res_geo["results"][0]["longitude"]
                
                params_clima = {"latitude": lat, "longitude": lon, "daily": "precipitation_probability_max", "current_weather": "true", "timezone": "America/Bogota"}
                datos_cl = requests.get("https://api.open-meteo.com/v1/forecast", params=params_clima).json()
                
                t_act, p_lluvia = datos_cl['current_weather']['temperature'], datos_cl['daily']['precipitation_probability_max'][0]
                
                st.subheader(f"Diagnóstico Climático en: {municipio}, {departamento}")
                st.markdown(f"**Temperatura actual:** {t_act} °C | **Probabilidad de lluvia:** {p_lluvia}%")
                
                # Reglas estrictas de decisión clínica del concreto.
                if p_lluvia > 50:
                    st.error("ALERTA: Alta probabilidad de precipitación en la zona de obra.")
                    st.markdown("**Recomendación técnica:** Es estrictamente necesario el uso de un aditivo **Acelerante**. Este evitará el deslave de la mezcla fresca por la lluvia al reducir el tiempo de fraguado.")
                elif t_act > 28:
                    st.warning("ALERTA: Temperaturas elevadas detectadas en la zona de obra.")
                    st.markdown("**Recomendación técnica:** Es necesario el uso de un aditivo **Plastificante** o **Retardante**. Las altas temperaturas evaporan el agua de curado rápidamente, y el aditivo mantendrá la mezcla manejable previniendo fisuras.")
                else:
                    st.success("Condiciones climáticas óptimas para el vaciado de concreto.")
                    st.markdown("**Recomendación técnica:** No es necesario el uso de aditivos adicionales por factores climáticos. Proceda con el diseño estándar y el curado convencional con agua.")
            except:
                st.warning("No se pudo conectar al servidor meteorológico en este momento. Verifique las condiciones manualmente.")
