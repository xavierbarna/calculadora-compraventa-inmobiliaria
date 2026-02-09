import streamlit as st
import google.generativeai as genai
from urllib.parse import quote

st.set_page_config(page_title="InmoReal AI - Cataluña", page_icon="🏢", layout="wide")

# --- CONFIGURACIÓN LOCAL ---
POBLACIONES = ["Barcelona", "Gavá", "Viladecans", "El Prat de Llobregat", "Molins de Rei", "Sant Feliu de Llobregat"]

BARRIOS_POR_POB = {
    "Barcelona": ["Sant Antoni", "Eixample", "Gràcia", "Poblenou", "Sarrià", "Sants", "Les Corts", "Horta", "Sant Martí"],
    "Gavá": ["Gavá Mar", "Centro", "Bruguers", "Diagonal - Colomeres"],
    "Viladecans": ["Centro", "Sales", "Alba-rosa", "Torrent Ballester"],
    "El Prat de Llobregat": ["Centro", "Eixample", "Verge de Montserrat"],
    "Molins de Rei": ["Centro", "El Canal", "Riera Bonet", "La Granja"],
    "Sant Feliu de Llobregat": ["Centre", "Mas Lluí", "Can Maginàs", "Les Grases"]
}

ITP_CATALUNYA = 0.10

def obtener_mejor_modelo(api_key):
    try:
        genai.configure(api_key=api_key)
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                return m.name
        return "models/gemini-1.5-flash"
    except:
        return "models/gemini-1.5-flash"

def consultar_ia(prompt, api_key):
    try:
        nombre_modelo = obtener_mejor_modelo(api_key)
        model = genai.GenerativeModel(nombre_modelo)
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error técnico: {str(e)}"

# --- INTERFAZ ---
st.title("⚖️ Consultor Inmobiliario: Área de Barcelona")

with st.sidebar:
    mi_api = st.text_input("API Key de Google", type="password")
    st.divider()
    st.header("1. Datos de Venta")
    pob_v = st.selectbox("Ciudad Venta", POBLACIONES)
    bar_v = st.selectbox("Barrio Venta", BARRIOS_POR_POB[pob_v])
    m2_v = st.number_input("M2 del piso actual", value=80)
    
    st.divider()
    st.header("2. Datos de Compra")
    pob_c = st.selectbox("Ciudad Destino", POBLACIONES, index=1)
    bar_c = st.selectbox("Barrio Destino", BARRIOS_POR_POB[pob_c])
    
    st.divider()
    st.header("3. Estrategia")
    pct_reinv = st.slider("% del neto para reinvertir", 10, 100, 85)
    comision_inmo = st.number_input("% Comisión Inmo Venta", value=3.0)

if st.button("REALIZAR ANÁLISIS DE MERCADO"):
    if not mi_api:
        st.error("Introduce la API Key.")
    else:
        with st.spinner('Calculando con ajuste del 8% sobre oferta...'):
            # Lógica de precio ajustado
            prompt_precio = f"""
            Como experto inmobiliario en Cataluña: 
            1. Busca el precio medio de oferta actual en portales para {bar_v}, {pob_v}. 
            2. Aplica una reducción del 8% por margen de negociación. 
            3. Responde SOLO con el número final por m2.
            """
            res_p1 = consultar_ia(prompt_precio, mi_api)
            
            try:
                precio_m2_v = float(''.join(filter(lambda x: x.isdigit() or x == '.', res_p1)))
            except:
                precio_m2_v = 4500.0

            # Cálculos
            v_total = precio_m2_v * m2_v
            gastos_v = (v_total * (comision_inmo/100)) + (v_total * 0.025) + 1500
            neto_disponible = v_total - gastos_v
            presupuesto_total_compra = neto_disponible * (pct_reinv / 100)
            ahorro_caja = neto_disponible - presupuesto_total_compra
            
            gastos_adquisicion = ITP_CATALUNYA + 0.015
            valor_max_inmueble = presupuesto_total_compra / (1 + gastos_adquisicion)

            # Recomendación
            prompt_rec = f"Presupuesto {valor_max_inmueble:,.0f}€ en {bar_c}, {pob_c}. ¿Qué puedo comprar? (m2, hab, estado)."
            recomendacion = consultar_ia(prompt_rec, mi_api)

            # --- RESULTADOS ---
            st.success("### Análisis Estratégico Finalizado")
            c1, c2, c3 = st.columns(3)
            c1.metric("Venta Bruta", f"{v_total:,.0f} €", f"{precio_m2_v:,.0f} €/m2")
            c2.metric("Para Compra", f"{presupuesto_total_compra:,.0f} €")
            c3.metric("AHORRO LÍQUIDO", f"{ahorro_caja:,.0f} €")

            st.divider()
            st.subheader(f"🏠 Posibilidades en {bar_c}")
            st.info(recomendacion)

            # --- BOTÓN WHATSAPP ---
            texto_wa = f"Análisis Inmobiliario:\n- Venta en {bar_v}: {v_total:,.0f}€\n- Neto disponible: {neto_disponible:,.0f}€\n- Presupuesto compra: {presupuesto_total_compra:,.0f}€\n- Ahorro final: {ahorro_caja:,.0f}€"
            wa_link = f"https://wa.me/?text={quote(texto_wa)}"
            st.markdown(f'[![Compartir en WhatsApp](https://img.shields.io/badge/Compartir_por-WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)]({wa_link})')

            with st.expander("Ver detalle técnico"):
                st.write(f"Precio m2 tras descuento 8%: {precio_m2_v:,.0f}€")
                st.write(f"Impuestos compra reservados: {presupuesto_total_compra - valor_max_inmueble:,.0f}€")
