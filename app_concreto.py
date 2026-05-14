# Importa Streamlit: la librería principal para construir la interfaz visual de la página web.
import streamlit as st 
# Importa Pandas: librería matemática para crear y manipular tablas de datos (DataFrames).
import pandas as pd 
# Importa Plotly Express: librería para dibujar gráficas interactivas (barras, tortas, etc.).
import plotly.express as px 
# Importa Base64: herramienta nativa de Python para transformar archivos (como imágenes) en texto legible para la web.
import base64 
# Importa Requests: librería para hacer peticiones HTTP (conectarse a internet para descargar datos de APIs).
import requests 

"""
Función del programa: APLICACIÓN WEB PARA DISEÑO DE MEZCLAS (VERSIÓN PRO)
Autor: Ing. Civiles Andrés Felipe Madroñero Garces & José Manuel Arboleda Carvajal.
"""

# Configura la pestaña del navegador: título de la página y layout "wide" para que ocupe todo el ancho de la pantalla.
st.set_page_config(page_title="Calculadora NSR-10 PRO", layout="wide")

# ==========================================
# 1. ESTÉTICA Y DISEÑO UI MEJORADO (CSS)
# ==========================================
# Definimos una función para inyectar diseño web (CSS) personalizado.
def cargar_estilos_y_fondo():
    try: # Intenta ejecutar este bloque; si el archivo no existe, pasará al 'except' para evitar que el programa colapse.
        # Abre la imagen 'fondo2.png' en modo lectura binaria ('rb').
        with open("fondo2.png", "rb") as image_file:
            # Codifica la imagen a texto base64 para que el navegador web pueda leerla como un fondo CSS.
            imagen_base64 = base64.b64encode(image_file.read()).decode()
            
        # Variable que guarda código CSS puro (el lenguaje de diseño de páginas web).
        css = f"""
        <style>
        .stApp {{
            /* Asigna la imagen codificada como fondo de toda la aplicación */
            background-image: url(data:image/png;base64,{imagen_base64});
            background-size: cover; /* Ajusta la imagen para cubrir toda la pantalla */
            background-position: center; /* Centra la imagen */
            background-attachment: fixed; /* Evita que el fondo se mueva al hacer scroll */
        }}
        /* Diseño de los contenedores (pestañas, cajas de texto, números) */
        .stTabs, .stSelectbox, .stNumberInput {{
            background-color: rgba(245, 247, 250, 0.95) !important; /* Fondo casi blanco para dar contraste */
            padding: 15px; /* Espacio interior */
            border-radius: 12px; /* Bordes redondeados */
            border: 2px solid #2980B9; /* Borde azul */
            box-shadow: 0px 4px 15px rgba(0,0,0,0.2); /* Sombra 3D */
        }}
        /* Reglas para hacer el texto más grueso y legible */
        html, body, p, div, span, label {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif !important;
            font-weight: 600 !important; /* Letra seminegrita */
            color: #1a252f; /* Color gris oscuro/negro */
        }}
        /* Reglas para los títulos principales (h1, h2, h3) */
        h1, h2, h3 {{
            color: #1A5276 !important; /* Azul oscuro */
            font-weight: 900 !important; /* Letra extra negrita */
            text-transform: uppercase; /* Convierte todo a MAYÚSCULAS */
            letter-spacing: 1px; /* Separación entre letras */
            text-shadow: 2px 2px 4px rgba(255,255,255,0.9); /* Sombra blanca para resaltar sobre el fondo */
        }}
        .stAlert {{ font-weight: 800 !important; }} /* Texto de alertas más grueso */
        </style>
        """
        # st.markdown inyecta el CSS en la página. 'unsafe_allow_html=True' autoriza el uso de etiquetas HTML/CSS directas.
        st.markdown(css, unsafe_allow_html=True)
    except FileNotFoundError:
        pass # Si no encuentra la imagen 'fondo2.png', ignora el error silenciosamente y muestra fondo blanco.

# Ejecutamos la función de diseño que acabamos de crear.
cargar_estilos_y_fondo()

# ==========================================
# 2. BASES DE DATOS (MUNICIPIOS Y PRECIOS)
# ==========================================

# @st.cache_data guarda el resultado en la memoria RAM del servidor. Así no se descarga de internet cada vez que se presiona un botón.
@st.cache_data
def obtener_municipios_colombia():
    try:
        # Enlace a la API pública de Colombia con formato JSON.
        url = "https://www.datos.gov.co/resource/xdk5-pm3f.json?$limit=1200"
        # Descarga los datos de internet.
        datos = requests.get(url).json()
        # Convierte los datos descargados en una tabla (DataFrame) para organizarlos fácilmente.
        df = pd.DataFrame(datos)
        # Agrupa la tabla por 'departamento' y asocia una lista de sus 'municipios'. Lo convierte en un diccionario.
        return df.groupby('departamento')['municipio'].apply(list).to_dict()
    except:
        # Si la página del gobierno cae, devuelve estos datos falsos como plan de respaldo para no dañar la app.
        return {"Bogotá D.C.": ["Bogotá"], "Quindío": ["Armenia"]}

# Ejecuta la función y guarda el diccionario de Colombia en la variable.
diccionario_lugares = obtener_municipios_colombia()
# Extrae solo los nombres de los departamentos, los ordena alfabéticamente (sorted) y los convierte en lista.
lista_departamentos = sorted(list(diccionario_lugares.keys()))
# Inserta el texto "Seleccione..." en la posición 0 (el principio) de la lista.
lista_departamentos.insert(0, "Seleccione...")

# Diccionario simple: Relaciona la marca de cemento (llave) con su precio por bulto (valor).
precios_cemento = {
    "Argos": 33500, "Cemex": 32000, "Holcim": 34000, "Sika": 45000 
}

# Diccionario anidado: Relaciona la marca, y dentro de ella, relaciona el tipo de aditivo con su precio.
precios_aditivos = {
    "Argos": {"Acelerante": 8000, "Retardante": 7500, "Plastificante": 9000, "Para juntas frías": 11000},
    "Cemex": {"Acelerante": 7800, "Retardante": 7200, "Plastificante": 8800, "Para juntas frías": 10500},
    "Holcim": {"Acelerante": 8200, "Retardante": 7600, "Plastificante": 9200, "Para juntas frías": 11500},
    "Sika": {"Acelerante": 12000, "Retardante": 11000, "Plastificante": 13000, "Para juntas frías": 15000}
}

# Variable del costo del agua (es fijo a nivel nacional para este ejemplo).
precio_agua_litro = 3.5 
# Diccionario anidado con los precios estimados de materiales por departamento.
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
    "San Andrés": {"arena": 120000, "trit": 130000}, "Santander": {"arena": 44000, "trit": 48000},
    "Sucre": {"arena": 38000, "trit": 42000}, "Tolima": {"arena": 46000, "trit": 51000},
    "Valle del Cauca": {"arena": 45000, "trit": 49000}, "Vaupés": {"arena": 95000, "trit": 100000},
    "Vichada": {"arena": 85000, "trit": 90000}
}

# ==========================================
# 3. LÓGICA MATEMÁTICA Y DE COSTOS
# ==========================================

# Función auxiliar para redondear números de forma inteligente.
def formatear_numero(valor):
    if valor == 0: return "0" # Si es exactamente cero, devuelve cero.
    if valor < 0.01: return f"{valor:.4f}" # Si es menor a 0.01 (minúsculo), usa 4 decimales.
    if valor < 0.1: return f"{valor:.3f}"  # Si es menor a 0.1 (pequeño), usa 3 decimales.
    return f"{valor:.2f}" # Para valores normales, usa 2 decimales estándar.

# Función principal que recibe todos los parámetros de la interfaz para hacer los cálculos.
def calcular_mezcla(resistencia, volumen, unidades, depto_seleccionado, marca_cem, marca_adi, tipo_adi, recipiente):
    
    # Condición en una sola línea: Divide entre 1000 si el usuario eligió Litros, sino lo deja igual (m3).
    volumen_m3 = volumen / 1000 if unidades == "Litros (L)" else volumen

    # Evaluador de dosificación según la resistencia seleccionada.
    if resistencia == "2500 PSI":
        cem_kg, arena_m3, trit_m3, agua_l = 300 * volumen_m3, 0.50 * volumen_m3, 0.70 * volumen_m3, 170 * volumen_m3
    elif resistencia == "3000 PSI":
        cem_kg, arena_m3, trit_m3, agua_l = 350 * volumen_m3, 0.45 * volumen_m3, 0.70 * volumen_m3, 180 * volumen_m3
    else: 
        cem_kg, arena_m3, trit_m3, agua_l = 420 * volumen_m3, 0.40 * volumen_m3, 0.70 * volumen_m3, 200 * volumen_m3

    vol_aditivo_L = 0
    # Evaluador para calcular la cantidad de aditivo requerida según el tipo.
    if tipo_adi == "Acelerante": vol_aditivo_L = (cem_kg * 0.02)
    elif tipo_adi == "Retardante": vol_aditivo_L = (cem_kg * 0.015) 
    elif tipo_adi == "Plastificante": vol_aditivo_L = (cem_kg * 0.01)
    elif tipo_adi == "Para juntas frías": vol_aditivo_L = (cem_kg * 0.012)

    # El método '.get()' busca el departamento en el diccionario. Si no lo encuentra, usa Antioquia por defecto para evitar errores.
    precio_arena_m3 = precios_regionales.get(depto_seleccionado, {"arena": 45000})["arena"]
    precio_trit_m3 = precios_regionales.get(depto_seleccionado, {"trit": 50000})["trit"]

    # Diccionario vacío para guardar los costos finales de cada marca.
    costos_totales = {}
    
    # Bucle 'for': Recorre (itera) las 4 marcas de cemento una por una.
    for marca in precios_cemento.keys():
        bultos = cem_kg / 50 # Convierte KG a bultos de 50kg.
        # Multiplica los bultos por el precio de la marca actual del bucle.
        costo_cemento_total = bultos * precios_cemento[marca]
        # Suma los costos de arena, triturado y agua.
        costo_agregados = (arena_m3 * precio_arena_m3) + (trit_m3 * precio_trit_m3) + (agua_l * precio_agua_litro)
        
        costo_aditivo_total = 0
        # Verifica si el usuario pidió aditivo. Si es "Ninguno", se queda en 0.
        if tipo_adi != "Ninguno":
            # Busca en el diccionario anidado el precio de la marca y tipo específico y lo multiplica por los litros.
            costo_aditivo_total = vol_aditivo_L * precios_aditivos[marca_adi][tipo_adi]
            
        # Suma todo y lo guarda en el diccionario bajo el nombre de la marca actual.
        costos_totales[marca] = costo_cemento_total + costo_agregados + costo_aditivo_total

    bultos_req = cem_kg / 50
    # Verifica si el usuario seleccionó un recipiente distinto a las unidades métricas estándar.
    if recipiente != "Unidades Estándar (m³, Litros, Bultos)":
        # Toma el texto "19 Litros", lo divide (split) por el espacio, toma el número "19" y lo convierte a entero (int).
        vol_recipiente = int(recipiente.split(" ")[0]) 
        # Divide los volúmenes totales entre el tamaño del recipiente para saber cuántos baldes necesita.
        baldes_arena, baldes_trit, baldes_agua = (arena_m3 * 1000) / vol_recipiente, (trit_m3 * 1000) / vol_recipiente, agua_l / vol_recipiente
        
        # Asigna la palabra "cuñetes" si el usuario eligió la opción de 19L, de lo contrario asume "baldes".
        unidad_rec = "cuñetes" if "Cuñete" in recipiente else "baldes"
            
        # Crea un diccionario con los textos finales que se verán en pantalla (usando la función de formateo para redondear).
        resultados_texto = {
            "Cemento": f"{formatear_numero(bultos_req)} Bultos (50kg)",
            "Arena": f"{formatear_numero(baldes_arena)} {unidad_rec}",
            "Triturado": f"{formatear_numero(baldes_trit)} {unidad_rec}",
            "Agua": f"{formatear_numero(baldes_agua)} {unidad_rec}",
            "Aditivo": f"{formatear_numero(vol_aditivo_L)} L" if vol_aditivo_L > 0 else "N/A"
        }
    else:
        # Crea el diccionario con unidades estándar (m3, Litros).
        resultados_texto = {
            "Cemento": f"{formatear_numero(bultos_req)} Bultos",
            "Arena": f"{formatear_numero(arena_m3)} m³",
            "Triturado": f"{formatear_numero(trit_m3)} m³",
            "Agua": f"{formatear_numero(agua_l)} Litros",
            "Aditivo": f"{formatear_numero(vol_aditivo_L)} L" if vol_aditivo_L > 0 else "N/A"
        }

    # La función devuelve dos cosas: los textos a imprimir y la tabla matemática de costos.
    return resultados_texto, costos_totales

# ==========================================
# 4. INTERFAZ WEB (FRONTEND)
# ==========================================

# Muestra el título y una descripción de la página en formato Markdown (texto enriquecido).
st.title("🏗️ Calculadora de Concreto NSR-10 PRO")
st.markdown("### Plataforma avanzada para el diseño de mezclas, análisis de costos regionales y diagnóstico climático.")

# Divide la pantalla principal en dos pestañas navegables.
tab_config, tab_resultados = st.tabs(["⚙️ CONFIGURACIÓN DE LA MEZCLA", "📊 RESULTADOS Y ANÁLISIS"])

# Bloque de código que se ejecutará solo dentro de la primera pestaña.
with tab_config:
    st.subheader("1. Ubicación de la Obra (Costos y Clima)")
    # Divide esa sección en 2 columnas verticales.
    col_dep, col_mun = st.columns(2)
    # Columna izquierda: Menú desplegable alimentado por la lista de departamentos.
    with col_dep:
        departamento = st.selectbox("Seleccione el Departamento:", lista_departamentos)
    # Columna derecha: Depende lógicamente de la columna izquierda.
    with col_mun:
        if departamento != "Seleccione...":
            # Si eligió un departamento válido, muestra los municipios correspondientes de ese departamento.
            municipio = st.selectbox("Seleccione el Municipio:", ["Seleccione..."] + sorted(diccionario_lugares[departamento]))
        else:
            # Si no ha elegido departamento, bloquea el selector pidiendo que lo haga.
            municipio = st.selectbox("Seleccione el Municipio:", ["Seleccione un departamento primero"])
            
    st.markdown("---") # st.markdown("---") dibuja una línea horizontal separadora.
    st.subheader("2. Parámetros Estructurales")
    # Divide esta sección en 3 columnas.
    col1, col2, col3 = st.columns(3)
    with col1:
        resistencia = st.selectbox("Resistencia (Compresión):", ["2500 PSI", "3000 PSI", "4000 PSI"])
    with col2:
        unidades = st.selectbox("Unidades de volumen:", ["Metros Cúbicos (m³)", "Litros (L)"])
    with col3:
        # st.number_input crea una caja para escribir números. format="%.4f" permite ingresar hasta 4 decimales.
        volumen = st.number_input("Volumen requerido:", min_value=0.001, value=1.0, step=0.1, format="%.4f")

    st.markdown("---")
    st.subheader("3. Especificaciones de Materiales")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        # Bucle interno (List comprehension): Crea un texto fusionando el nombre de la marca y su precio para mostrarlo en el selector.
        lista_marcas_cem = [f"{marca} (${precio:,.0f}/bulto)" for marca, precio in precios_cemento.items()]
        marca_cemento = st.selectbox("Marca de Cemento:", lista_marcas_cem)
        # Extrae solo la primera palabra (ej. "Argos" de "Argos ($33,500/bulto)") para enviarla a los cálculos.
        marca_pura_cem = marca_cemento.split(" ")[0] 
    with col_m2:
        marca_aditivo = st.selectbox("Marca del Aditivo:", ["Argos", "Cemex", "Holcim", "Sika"])
    with col_m3:
        tipo_aditivo = st.selectbox("Tipo de Aditivo:", ["Ninguno", "Acelerante", "Retardante", "Plastificante", "Para juntas frías"])
        
    recipiente = st.selectbox("Herramienta de Medición en Obra:", [
        "Unidades Estándar (m³, Litros, Bultos)", "19 Litros (Cuñete de pintura)",
        "12 Litros (Balde negro grande)", "10 Litros (Balde negro mediano)"
    ])

# Bloque de código que se ejecutará solo dentro de la segunda pestaña.
with tab_resultados:
    st.subheader("Cantidades Matemáticas Exactas")
    
    # Previene que la aplicación haga cálculos y arroje errores si el usuario no ha completado el paso 1.
    if departamento == "Seleccione...":
        st.warning("⚠️ Por favor seleccione un Departamento en la pestaña de Configuración para calcular los costos regionales.")
    else:
        # Llama a la función matemática y guarda sus dos respuestas en las variables 'resultados' y 'costos'.
        resultados, costos = calcular_mezcla(resistencia, volumen, unidades, departamento, marca_pura_cem, marca_aditivo, tipo_aditivo, recipiente)
        
        # Divide el espacio en 5 columnas delgadas para mostrar los 5 materiales.
        c1, c2, c3, c4, c5 = st.columns(5)
        # Usa cuadros de colores (info, success, warning, error) para mostrar los datos del diccionario.
        c1.info(f"**CEMENTO**\n\n{resultados['Cemento']}")
        c2.success(f"**ARENA**\n\n{resultados['Arena']}")
        c3.warning(f"**TRITURADO**\n\n{resultados['Triturado']}")
        c4.info(f"**AGUA**\n\n{resultados['Agua']}")
        c5.error(f"**ADITIVO**\n\n{resultados['Aditivo']}")
        
        st.markdown("---")
        st.subheader(f"Comparativa de Costos (Precios promediados para {departamento})")
        
        # Crea un DataFrame (Tabla) de Pandas con los resultados de la variable 'costos' para dárselo a la gráfica.
        df_costos = pd.DataFrame({
            "Marca Estructural": list(costos.keys()),
            "Costo Total (COP)": list(costos.values())
        })
        
        # px.bar dibuja una gráfica de barras indicando los colores y qué datos van en el eje X y Y.
        fig = px.bar(df_costos, x="Marca Estructural", y="Costo Total (COP)", 
                     text="Costo Total (COP)", color="Marca Estructural",
                     color_discrete_sequence=["#1ABC9C", "#3498DB", "#E74C3C", "#F1C40F"],
                     title="Costo final de la mezcla incluyendo agregados y aditivos")
        # Ajusta el texto de la gráfica para mostrar el signo de moneda '$'.
        fig.update_traces(texttemplate='$%{text:,.0f}', textposition='outside', textfont=dict(size=14, color='black'))
        fig.update_layout(uniformtext_minsize=12, uniformtext_mode='hide', plot_bgcolor="rgba(255,255,255,0.8)")
        # Muestra la gráfica renderizada en Streamlit ocupando todo el ancho disponible.
        st.plotly_chart(fig, use_container_width=True)

        # ==========================================
        # DIAGNÓSTICO CLIMÁTICO
        # ==========================================
        st.markdown("---")
        # Asegura que haya un municipio válido para buscar su clima.
        if municipio != "Seleccione...":
            try: # Bloque de protección. Si falla el internet, no se crashea el programa, salta al 'except'.
                # Parámetros para buscar las coordenadas de la ciudad de forma segura.
                params_geo = {"name": municipio, "count": 1, "language": "es"}
                res_geo = requests.get("https://geocoding-api.open-meteo.com/v1/search", params=params_geo).json()
                lat, lon = res_geo["results"][0]["latitude"], res_geo["results"][0]["longitude"]
                
                # Parámetros para buscar el clima exacto en esas coordenadas.
                params_clima = {"latitude": lat, "longitude": lon, "daily": "precipitation_probability_max", "current_weather": "true", "timezone": "America/Bogota"}
                datos_cl = requests.get("https://api.open-meteo.com/v1/forecast", params=params_clima).json()
                
                # Extrae de la base de datos la temperatura y la probabilidad de lluvia.
                t_act, p_lluvia = datos_cl['current_weather']['temperature'], datos_cl['daily']['precipitation_probability_max'][0]
                
                st.subheader(f"☁️ Diagnóstico Climático en: {municipio}, {departamento}")
                st.markdown(f"**Temperatura actual:** {t_act} °C | **Probabilidad de lluvia:** {p_lluvia}%")
                
                # Lógica de decisión técnica (Alerte si es mayor a 50% lluvia o mayor a 28C calor).
                if p_lluvia > 50:
                    st.error("### 🔴 ALERTA: Alta probabilidad de lluvia.")
                elif t_act > 28:
                    st.warning("### 🟠 ALERTA: Temperaturas elevadas detectadas.")
                else:
                    st.success("### 🟢 Condiciones óptimas para vaciado.")
            except:
                st.warning("No se pudo conectar al satélite del clima.")
