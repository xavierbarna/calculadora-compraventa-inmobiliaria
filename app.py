import streamlit as st
import google.generativeai as genai
from datetime import date

st.set_page_config(page_title="InmoReal AI Pro", page_icon="🏢", layout="wide")

# Diccionario de barrios (¡Ahora corregido para que Compra y Venta sean independientes!)
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
    try:
        genai.configure(api_key=api_key)
        # CAMBIO CLAVE: Usamos el modelo 1.5 flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error en la consulta: {str(e)}"

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
    pct_reinv = st.slider("% de reinversión del neto para la compra", 10, 100, 80)
    comision_inmo = st.number_input("% Comisión Inmobiliaria", value=3.0)

if st.button("ANALIZAR OPERACIÓN"):
    if not mi_api:
        st.error("Por favor, introduce tu API Key en la barra lateral.")
    else:
        with st.spinner('Analizando mercado con Gemini 1.5...'):
            # Prompt para el precio de venta (más agresivo para evitar fallos)
            p1 = f"Precio medio REAL de cierre por m2 en {bar_v}, {pob_v} (España) en 2024. Responde SOLO con el número, sin texto."
            res_p1 = consultar_ia(p1, mi_api)
            
            try:
                precio_m2_v = float(''.join(filter(lambda x: x.isdigit() or x == '.', res_p1)))
            except:
                precio_m2_v = 5500.0 # Valor de rescate coherente para BCN/MAD

            # Cálculos Financieros
            v_total = precio_m2_v * m2_v
            # Gastos: Inmo + Plusvalía Mun (est 2%) + Notaría/Registro (est 1.5k)
            gastos_v = (v_total * (comision_inmo/100)) + (v_total * 0.025) + 1500
            neto_disponible = v_total - gastos_v
            
            presupuesto_compra_total = neto_disponible * (pct_reinv / 100)
            ahorro_liquido = neto_disponible - presupuesto_compra_total
            
            # Cálculo de lo que se puede pagar por el piso (restando ITP y gastos de la CCAA destino)
            tasa_impuestos_compra = ITP_DICT[ccaa_c] + 0.015 # ITP + 1.5% notaría/registro
            valor_max_inmueble = presupuesto_compra_total / (1 + tasa_impuestos_compra)

            # Prompt para la recomendación descriptiva
            p2 = f"""En el barrio de {bar_c}, {pob_c}, con un presupuesto total de {valor_max_inmueble:,.0f} euros, 
            ¿qué tipo de vivienda exacta se puede comprar hoy? Describe metros, habitaciones, estado y si incluye extras como garaje. 
            Sé muy realista con el mercado actual."""
            recomendacion = consultar_ia(p2, mi_api)

            # --- RESULTADOS ---
            st.success("### Análisis Estratégico Finalizado")
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Venta Estimada", f"{v_total:,.0f} €", f"{precio_m2_v:,.0f} €/m2")
            col2.metric("Disponible para Compra", f"{presupuesto_compra_total:,.0f} €", f"{pct_reinv}% del neto")
            col3.metric("AHORRO NETO", f"{ahorro_liquido:,.0f} €", delta="Dinero sobrante")

            st.divider()
            
            st.subheader(f"🏠 Perfil de vivienda en {bar_c} ({pob_c})")
            st.markdown(recomendacion)
            
            with st.expander("Ver desglose de impuestos y gastos"):
                st.write(f"Venta Bruta: {v_total:,.0f} €")
                st.write(f"Gastos Venta (Inmo+Impuestos): -{gastos_v:,.0f} €")
                st.write(f"Neto tras venta: {neto_disponible:,.0f} €")
                st.write(f"---")
                st.write(f"Precio del inmueble destino: {valor_max_inmueble:,.0f} €")
                st.write(f"Impuestos y gastos compra ({ccaa_c}): {presupuesto_compra_total - valor_max_inmueble:,.0f} €")
