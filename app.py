import streamlit as st
import google.generativeai as genai
from datetime import date

st.set_page_config(page_title="InmoReal AI Pro", page_icon="🏢", layout="wide")

# Diccionario de barrios
ZONAS = {
    "Barcelona": ["Sant Antoni", "Eixample", "Gràcia", "Poblenou", "Sarrià", "Sants", "Les Corts"],
    "Madrid": ["Salamanca", "Chamberí", "Retiro", "Tetuán", "Hortaleza", "Usera", "Arganzuela"],
    "Valencia": ["Ruzafa", "Ciutat Vella", "El Carmen", "Patraix", "Benimaclet", "Campanar"],
    "Alicante": ["Centro", "Playa de San Juan", "Cabo de las Huertas", "Carolinas", "Benalúa"]
}

ITP_DICT = {
    "Cataluña": 0.10, "Madrid": 0.06, "Comunidad Valenciana": 0.10, "Andalucía": 0.07,
    "Aragón": 0.08, "Baleares": 0.08, "Canarias": 0.065, "País Vasco": 0.04
}

def obtener_mejor_modelo(api_key):
    try:
        genai.configure(api_key=api_key)
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
        return "models/gemini-pro" # Fallback
    except:
        return "models/gemini-pro"

def consultar_ia(prompt, api_key):
    try:
        genai.configure(api_key=api_key)
        nombre_modelo = obtener_mejor_modelo(api_key)
        model = genai.GenerativeModel(nombre_modelo)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error técnico tras intentar conectar: {str(e)}"

# --- INTERFAZ ---
st.title("⚖️ Estrategia de Inversión Inmobiliaria Inteligente")

with st.sidebar:
    mi_api = st.text_input("API Key de Google", type="password")
    st.divider()
    
    st.header("1. Datos de Venta")
    ccaa_v = st.selectbox("CCAA Venta", list(ITP_DICT.keys()), index=0)
    pob_v = st.selectbox("Ciudad Venta", list(ZONAS.keys()), index=0)
    bar_v = st.selectbox("Barrio Venta", ZONAS[pob_v])
    m2_v = st.number_input("M2 del piso actual", value=100)
    
    st.divider()
    st.header("2. Datos de Compra")
    ccaa_c = st.selectbox("CCAA Compra", list(ITP_DICT.keys()), index=2)
    pob_c = st.selectbox("Ciudad Compra", list(ZONAS.keys()), index=3)
    bar_c = st.selectbox("Barrio Destino", ZONAS[pob_c])
    
    st.divider()
    st.header("3. Estrategia")
    pct_reinv = st.slider("% del neto para comprar", 10, 100, 80)
    comision_inmo = st.number_input("% Comisión Inmobiliaria Venta", value=3.0)

if st.button("ANALIZAR OPERACIÓN"):
    if not mi_api:
        st.error("Introduce la API Key.")
    else:
        with st.spinner('Detectando modelo y analizando mercado...'):
            # Prompt de precio
            p1 = f"Dime solo el número del precio medio de cierre m2 en {bar_v}, {pob_v} en 2024. Sin texto."
            res_p1 = consultar_ia(p1, mi_api)
            
            try:
                precio_m2_v = float(''.join(filter(lambda x: x.isdigit() or x == '.', res_p1)))
            except:
                precio_m2_v = 5500.0 if "Barcelona" in pob_v else 4000.0

            # Cálculos
            v_total = precio_m2_v * m2_v
            gastos_v = (v_total * (comision_inmo/100)) + (v_total * 0.025) + 1500
            neto_disponible = v_total - gastos_v
            
            presupuesto_total_compra = neto_disponible * (pct_reinv / 100)
            ahorro_caja = neto_disponible - presupuesto_total_compra
            
            tasa_compra = ITP_DICT[ccaa_c] + 0.015 
            valor_max_piso = presupuesto_total_compra / (1 + tasa_compra)

            # Prompt recomendación
            p2 = f"Con {valor_max_piso:,.0f}€ en el barrio de {bar_c}, {pob_c}, ¿qué piso puedo comprar? Describe m2, hab y estado."
            recomendacion = consultar_ia(p2, mi_api)

            # RESULTADOS
            st.success("### Análisis Estratégico")
            c1, c2, c3 = st.columns(3)
            c1.metric("Venta Bruta", f"{v_total:,.0f} €")
            c2.metric("Para Compra", f"{presupuesto_total_compra:,.0f} €")
            c3.metric("AHORRO LÍQUIDO", f"{ahorro_caja:,.0f} €")

            st.divider()
            st.subheader(f"🏠 Mercado en {bar_c}")
            st.info(recomendacion)
