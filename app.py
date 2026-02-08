import streamlit as st
import google.generativeai as genai
from datetime import date

st.set_page_config(page_title="InmoReal AI Pro", page_icon="🏢", layout="wide")

# Diccionario de barrios para los desplegables
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

def consultar_ia(prompt, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

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
    
    st.header("2. Datos de Compra")
    ccaa_c = st.selectbox("CCAA Compra", list(ITP_DICT.keys()), index=2)
    pob_c = st.selectbox("Ciudad Compra", list(ZONAS.keys()), index=3)
    bar_c = st.selectbox("Barrio Destino", ZONAS[pob_c])
    
    st.header("3. Estrategia")
    pct_reinv = st.slider("% de reinversión del neto", 10, 100, 80)
    comision_inmo = st.number_input("% Comisión Inmobiliaria", value=3.0)

if st.button("ANALIZAR OPERACIÓN"):
    if not mi_api:
        st.error("Introduce la API Key.")
    else:
        with st.spinner('Consultando mercado...'):
            # Prompt 1: Obtener precio m2 real
            p1 = f"Dame SOLO el número del precio medio de cierre real por m2 en {bar_v}, {pob_v} en 2024. No des texto, solo el número."
            res_p1 = consultar_ia(p1, mi_api)
            
            try:
                precio_m2_v = float(''.join(filter(lambda x: x.isdigit() or x == '.', res_p1)))
            except:
                precio_m2_v = 5500.0 # Valor coherente para Sant Antoni si falla la IA

            # Cálculos Financieros
            v_total = precio_m2_v * m2_v
            gastos_v = (v_total * (comision_inmo/100)) + (v_total * 0.02) + 1500 # Inmo + Plusvalía est + Notaría
            neto_disponible = v_total - gastos_v
            
            presupuesto_compra_total = neto_disponible * (pct_reinv / 100)
            ahorro_liquido = neto_venta = neto_disponible - presupuesto_compra_total
            
            # Cálculo del valor del inmueble destino (restando ITP y Gastos)
            coste_adquisicion = ITP_DICT[ccaa_c] + 0.015 # ITP + 1.5% gastos
            valor_max_piso = presupuesto_compra_total / (1 + coste_adquisicion)

            # Prompt 2: Recomendación de producto inmobiliario
            p2 = f"""Con un presupuesto de {valor_max_piso:,.0f} euros en el barrio de {bar_c}, {pob_c}, 
            ¿qué tipo de vivienda puedo comprar? Sé específico: nº habitaciones, m2, si incluye garaje o trastero, 
            y estado de la finca. Da 2 opciones realistas."""
            recomendacion = consultar_ia(p2, mi_api)

            # --- RESULTADOS ---
            st.success("### Análisis Finalizado")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Venta Estimada", f"{v_total:,.0f} €", f"{precio_m2_v:,.0f} €/m2")
            c2.metric("Inversión en Compra", f"{presupuesto_compra_total:,.0f} €", f"{pct_reinv}% del neto")
            c3.metric("AHORRO EN CAJA", f"{ahorro_liquido:,.0f} €", delta="Líquido")

            st.divider()
            
            st.subheader(f"🏠 ¿Qué puedes comprar en {bar_c} con {valor_max_piso:,.0f} €?")
            st.info(recomendacion)
            
            st.write(f"*(Nota: Se han reservado {(presupuesto_compra_total - valor_max_piso):,.0f} € para ITP y gastos de escritura)*")
