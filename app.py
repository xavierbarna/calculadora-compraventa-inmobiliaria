{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh17040\viewkind0
\pard\tx566\tx1133\tx1700\tx2267\tx2834\tx3401\tx3968\tx4535\tx5102\tx5669\tx6236\tx6803\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import google.generativeai as genai\
\
# --- CONFIGURACI\'d3N ---\
st.set_page_config(page_title="InmoReal Calculator", page_icon="\uc0\u55356 \u57304 \u65039 ")\
\
# Diccionario de ITP por Comunidad Aut\'f3noma\
itp_dict = \{\
    "Andaluc\'eda": 0.07, "Arag\'f3n": 0.08, "Asturias": 0.08, "Baleares": 0.08,\
    "Canarias": 0.065, "Cantabria": 0.08, "Castilla y Le\'f3n": 0.08, \
    "Castilla-La Mancha": 0.09, "Catalu\'f1a": 0.10, "Comunidad Valenciana": 0.10,\
    "Extremadura": 0.08, "Galicia": 0.09, "Madrid": 0.06, "Murcia": 0.08,\
    "Navarra": 0.06, "Pa\'eds Vasco": 0.04, "La Rioja": 0.07\
\}\
\
def obtener_precio_real(comunidad, poblacion, barrio, api_key, es_venta=True):\
    genai.configure(api_key=api_key)\
    model = genai.GenerativeModel('gemini-pro')\
    \
    # Prompt espec\'edfico para evitar precios de portales inflados\
    tipo_op = "VENTA REAL" if es_venta else "COMPRA REAL"\
    prompt = f"""\
    Como experto en mercado inmobiliario espa\'f1ol, dime el precio medio por m2 de \{tipo_op\} \
    en el barrio de \{barrio\}, \{poblacion\} (\{comunidad\}). \
    No me des precios de portales inmobiliarios (anuncios). \
    Dame el precio estimado de CIERRE EN NOTAR\'cdA.\
    Responde exclusivamente con el n\'famero de euros, sin texto adicional.\
    """\
    try:\
        response = model.generate_content(prompt)\
        # Extraer solo el n\'famero\
        precio = float(''.join(filter(lambda x: x.isdigit() or x == '.', response.text)))\
        return precio\
    except:\
        return 2200.0\
\
# --- INTERFAZ STREAMLIT ---\
st.title("\uc0\u55356 \u57304 \u65039  Calculadora de Beneficio Real")\
st.markdown("Estimaci\'f3n basada en precios de cierre y fiscalidad auton\'f3mica.")\
\
with st.sidebar:\
    api_key = st.text_input("Clave API de Google", type="password")\
    st.info("La API se usa para consultar la base de datos de precios de mercado.")\
\
col1, col2 = st.columns(2)\
\
with col1:\
    st.header("1. Operaci\'f3n de Venta")\
    ccaa_v = st.selectbox("CCAA Venta", list(itp_dict.keys()), key="v1")\
    pob_v = st.text_input("Poblaci\'f3n Venta", "Madrid")\
    bar_v = st.text_input("Barrio Venta", "Tetu\'e1n")\
    m2_v = st.number_input("Metros cuadrados", value=80)\
\
with col2:\
    st.header("2. Operaci\'f3n de Compra")\
    ccaa_c = st.selectbox("CCAA Compra", list(itp_dict.keys()), key="c1")\
    pob_c = st.text_input("Poblaci\'f3n Compra", "Valencia")\
    bar_c = st.text_input("Barrio Compra", "Ruzafa")\
    pct_reinv = st.slider("% Reinversi\'f3n del neto", 0, 100, 100)\
\
if st.button("CALCULAR OPERACI\'d3N COMPLETA"):\
    if not api_key:\
        st.warning("Introduce la API Key para continuar.")\
    else:\
        with st.spinner('Analizando mercado y calculando impuestos...'):\
            # Venta\
            p_m2_v = obtener_precio_real(ccaa_v, pob_v, bar_v, api_key, True)\
            venta_total = p_m2_v * m2_v\
            plusvalia = venta_total * 0.03  # Estimaci\'f3n plusval\'eda municipal\
            neto_venta = venta_total - plusvalia\
            \
            # Compra\
            disponible_bruto = neto_venta * (pct_reinv / 100)\
            tasa_itp = itp_dict[ccaa_c]\
            \
            # C\'e1lculo del precio del piso quitando el ITP (Precio = Total / 1+ITP)\
            precio_max_piso = disponible_bruto / (1 + tasa_itp)\
            impuesto_compra = precio_max_piso * tasa_itp\
            \
            # Resultados\
            st.divider()\
            c1, c2, c3 = st.columns(3)\
            c1.metric("Venta Real (Cierre)", f"\{venta_total:,.0f\} \'80")\
            c2.metric("Neto tras Plusval\'eda", f"\{neto_venta:,.0f\} \'80")\
            c3.metric("Piso M\'e1ximo (Sin ITP)", f"\{precio_max_piso:,.0f\} \'80")\
            \
            st.success(f"**Impuestos totales de compra (ITP):** \{impuesto_compra:,.2f\} \'80")\
            \
            st.subheader(f"\uc0\u55357 \u56525  Relaci\'f3n de pisos en \{bar_c\} hasta \{precio_max_piso:,.0f\} \'80")\
            st.write("Basado en el presupuesto, podr\'edas optar a:")\
            st.info(f"1. Vivienda est\'e1ndar en \{bar_c\}: ~\{(precio_max_piso/obtener_precio_real(ccaa_c, pob_c, bar_c, api_key, False)):,.0f\} m\'b2")}