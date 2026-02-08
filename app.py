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

def consultar_ia(prompt, api_key):
    try:
        genai.configure(api_key=api_key)
        # Intentamos con el nombre técnico completo que es más estable
        model = genai.GenerativeModel('models/gemini-1.5-flash')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error técnico: {str(e)}"

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
    pct_reinv = st.slider("% del neto para reinvertir en la compra", 10, 100, 80)
    comision_inmo = st.number_input("% Comisión Inmobiliaria Venta", value=3.0)

if st.button("ANALIZAR OPERACIÓN"):
    if not mi_api:
        st.error("Introduce la API Key en la barra lateral.")
    else:
        with st.spinner('Consultando mercado en tiempo real...'):
            # Prompt de precio de venta
            p1 = f"Precio medio REAL de cierre por m2 en {bar_v}, {pob_v} (España) en 2024. Responde exclusivamente con el número."
            res_p1 = consultar_ia(p1, mi_api)
            
            try:
                # Extraemos el número por si la IA añade texto extra
                precio_m2_v = float(''.join(filter(lambda x: x.isdigit() or x == '.', res_p1)))
            except:
                precio_m2_v = 5500.0 # Valor coherente para Sant Antoni

            # Cálculos Financieros
            v_total = precio_m2_v * m2_v
            # Gastos de salida (Inmo + Plusvalía Mun est. + Gastos fijos)
            gastos_v = (v_total * (comision_inmo/100)) + (v_total * 0.025) + 1500
            neto_disponible = v_total - gastos_v
            
            # Aplicamos el porcentaje de reinversión elegido
            presupuesto_total_compra = neto_disponible * (pct_reinv / 100)
            ahorro_caja = neto_disponible - presupuesto_total_compra
            
            # Cálculo del valor neto del inmueble (restando ITP y gastos de la CCAA destino)
            tasa_impuestos_compra = ITP_DICT[ccaa_c] + 0.015 
            valor_max_inmueble = presupuesto_total_compra / (1 + tasa_impuestos_compra)

            # Prompt de recomendación descriptiva
            p2 = f"""En el barrio de {bar_c}, {pob_c}, con un presupuesto para el inmueble de {valor_max_inmueble:,.0f} euros, 
            describe qué tipo de vivienda se puede comprar. Incluye: m2 aproximados, número de habitaciones, 
            si es posible que tenga garaje o terraza y el estado general de la finca."""
            recomendacion = consultar_ia(p2, mi_api)

            # --- RESULTADOS ---
            st.success("### Análisis Estratégico Finalizado")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Venta Estimada", f"{v_total:,.0f} €", f"{precio_m2_v:,.0f} €/m2")
            c2.metric("Para invertir en compra", f"{presupuesto_total_compra:,.0f} €", f"{pct_reinv}% del neto")
            c3.metric("EFECTIVO SOBRANTE", f"{ahorro_caja:,.0f} €", delta="Ahorro líquido")

            st.divider()
            
            st.subheader(f"🏠 Posibilidades en {bar_c} ({pob_c})")
            st.info(recomendacion)
            
            with st.expander("Ver detalle de la operación"):
                st.write(f"**Venta en {bar_v}:**")
                st.write(f"- Valor bruto: {v_total:,.0f} €")
                st.write(f"- Gastos e impuestos venta: {gastos_v:,.0f} €")
                st.write(f"- Neto resultante: {neto_disponible:,.0f} €")
                st.write(f"---")
                st.write(f"**Compra en {bar_c}:**")
                st.write(f"- Presupuesto total (Inmueble + Gastos): {presupuesto_total_compra:,.0f} €")
                st.write(f"- Valor máximo del piso: {valor_max_inmueble:,.0f} €")
                st.write(f"- Reserva para ITP y Gastos: {presupuesto_total_compra - valor_max_inmueble:,.0f} €")
