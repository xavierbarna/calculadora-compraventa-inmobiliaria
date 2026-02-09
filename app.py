import streamlit as st
import google.generativeai as genai
from datetime import date

st.set_page_config(page_title="InmoReal AI - Cataluña", page_icon="🏢", layout="wide")

# --- CONFIGURACIÓN LOCAL (Cataluña) ---
POBLACIONES = [
    "Barcelona", 
    "Gavá", 
    "Viladecans", 
    "El Prat de Llobregat", 
    "Molins de Rei", 
    "Sant Feliu de Llobregat"
]

# Barrios por población (puedes ampliar estas listas si lo deseas)
BARRIOS_POR_POB = {
    "Barcelona": ["Sant Antoni", "Eixample", "L'Antiga Esquerra de l'Eixample", "La Nova Esquerra de l'Eixample"],
    "Gavá": ["Gavá Mar", "Centre", "Bruguers", "Diagonal", "Les Colomeres", "Bobiles", "Can Tintorer", "Can Tries"],
    "Viladecans": ["Centre", "Barri Antic", "Alba-rosa", "Torrent Ballester", "Campreciós", "Torre Roja", "La Roureda", "Llevant"],
    "El Prat de Llobregat": ["Centre", "Eixample", "Plaça de Catalunya", "Sant Jordi", "Estación"],
    "Molins de Rei": ["Centre", "El Canal", "Riera Bonet", "La Granja"],
    "Sant Feliu de Llobregat": ["Centre", "Mas Lluí", "Can Maginàs", "Les Grases", "Can Calders", "La Salut"]
}

ITP_CATALUNYA = 0.10  # 10% fijo para Cataluña

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
    st.info("📍 Región: Cataluña")
    pob_v = st.selectbox("Ciudad Venta", POBLACIONES)
    bar_v = st.selectbox("Barrio Venta", BARRIOS_POR_POB[pob_v])
    m2_v = st.number_input("M2 del piso actual", value=80)
    
    st.divider()
    st.header("2. Datos de Compra")
    pob_c = st.selectbox("Ciudad Destino", POBLACIONES, index=1) # Por defecto Gavá
    bar_c = st.selectbox("Barrio Destino", BARRIOS_POR_POB[pob_c])
    
    st.divider()
    st.header("3. Estrategia")
    pct_reinv = st.slider("% del neto para reinvertir", 10, 100, 85)
    comision_inmo = st.number_input("% Comisión Inmo Venta", value=3.0)

if st.button("REALIZAR ANÁLISIS DE MERCADO"):
    if not mi_api:
        st.error("Introduce la API Key.")
    else:
        with st.spinner('Analizando mercado local...'):
            # Prompt para precio venta
            p1 = f"Dime el precio medio real de cierre m2 en {bar_v}, {pob_v}, Cataluña, en 2024/2025. Responde SOLO con el número."
            res_p1 = consultar_ia(p1, mi_api)
            
            try:
                precio_m2_v = float(''.join(filter(lambda x: x.isdigit() or x == '.', res_p1)))
            except:
                precio_m2_v = 4000.0

            # Cálculos Financieros
            v_total = precio_m2_v * m2_v
            # Gastos venta: Inmo + Plusvalía Mun (2.5%) + Gastos Gestión (1500€)
            gastos_v = (v_total * (comision_inmo/100)) + (v_total * 0.025) + 1500
            neto_disponible = v_total - gastos_v
            
            presupuesto_total_compra = neto_disponible * (pct_reinv / 100)
            ahorro_caja = neto_disponible - presupuesto_total_compra
            
            # Cálculo valor inmueble destino (ITP 10% + 1.5% gastos)
            gastos_adquisicion = ITP_CATALUNYA + 0.015
            valor_max_inmueble = presupuesto_total_compra / (1 + gastos_adquisicion)

            # Prompt recomendación
            p2 = f"""Como experto inmobiliario en Cataluña: Con un presupuesto de {valor_max_inmueble:,.0f}€ 
            en el barrio de {bar_c}, {pob_c}, ¿qué tipo de vivienda exacta se puede comprar hoy? 
            Describe m2, habitaciones, estado típico de la finca y si es habitual que tenga extras como ascensor o balcón."""
            recomendacion = consultar_ia(p2, mi_api)

            # --- RESULTADOS ---
            st.success("### Resultado del Análisis Estratégico")
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Venta Bruta", f"{v_total:,.0f} €", f"{precio_m2_v:,.0f} €/m2")
            c2.metric("Para Compra", f"{presupuesto_total_compra:,.0f} €")
            c3.metric("EFECTIVO SOBRANTE", f"{ahorro_caja:,.0f} €", delta="Ahorro líquido")

            st.divider()
            
            st.subheader(f"🏠 Posibilidades en {bar_c} ({pob_c})")
            st.info(recomendacion)
            
            with st.expander("Ver detalle de gastos e impuestos"):
                st.write(f"**Operación Venta:**")
                st.write(f"- Gastos e impuestos estim.: {gastos_v:,.0f} €")
                st.write(f"- Neto obtenido: {neto_disponible:,.0f} €")
                st.write(f"---")
                st.write(f"**Operación Compra:**")
                st.write(f"- Precio máximo del piso: {valor_max_inmueble:,.0f} €")
                st.write(f"- Impuestos (ITP 10%) y Notaría: {presupuesto_total_compra - valor_max_inmueble:,.0f} €")
