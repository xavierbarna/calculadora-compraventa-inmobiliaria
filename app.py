import streamlit as st
import google.generativeai as genai
from datetime import date

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="InmoReal AI Pro", page_icon="🏦")

itp_dict = {
    "Andalucía": 0.07, "Aragón": 0.08, "Asturias": 0.08, "Baleares": 0.08,
    "Canarias": 0.065, "Cantabria": 0.08, "Castilla y León": 0.08, 
    "Castilla-La Mancha": 0.09, "Cataluña": 0.10, "Comunidad Valenciana": 0.10,
    "Extremadura": 0.08, "Galicia": 0.09, "Madrid": 0.06, "Murcia": 0.08,
    "Navarra": 0.06, "País Vasco": 0.04, "La Rioja": 0.07
}

def obtener_precio_real(comunidad, poblacion, barrio, api_key, es_venta=True):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    tipo = "VENTA" if es_venta else "COMPRA"
    prompt = f"Precio medio m2 de cierre real en {barrio}, {poblacion} ({comunidad}). Dame solo un número."
    try:
        response = model.generate_content(prompt)
        return float(''.join(filter(lambda x: x.isdigit() or x == '.', response.text)))
    except:
        return 2800.0

# --- INTERFAZ ---
st.title("🏦 Consultor de Inversión Inmobiliaria")

with st.sidebar:
    mi_api = st.text_input("API Key de Google Cloud", type="password")
    st.divider()
    
    st.subheader("📍 Datos de la Venta")
    ccaa_v = st.selectbox("Comunidad Autónoma", list(itp_dict.keys()))
    pob_v = st.text_input("Población", "Madrid")
    bar_v = st.text_input("Barrio o Zona específica", "Retiro")
    m2_v = st.number_input("Metros cuadrados", value=90)
    
    st.subheader("📅 Historial")
    fecha_compra = st.date_input("Fecha en que compraste el piso", value=date(2010, 1, 1))
    precio_compra_orig = st.number_input("¿Cuánto te costó en su día? (€)", value=150000)
    
    st.subheader("💸 Gastos de Venta")
    comision_inmo = st.slider("% Comisión Inmobiliaria", 0, 6, 3)

    st.divider()
    st.subheader("📍 Datos de la Compra")
    ccaa_c = st.selectbox("¿Dónde quieres comprar?", list(itp_dict.keys()))
    pob_c = st.text_input("Población destino", "Alicante")
    bar_c = st.text_input("Barrio destino", "Playa de San Juan")

# --- LÓGICA DE CÁLCULO ---
if st.button("CALCULAR OPERACIÓN COMPLETA"):
    if not mi_api:
        st.error("Por favor, introduce tu API Key.")
    else:
        with st.spinner('Analizando mercado y calculando impuestos...'):
            # 1. Análisis de Venta
            p_m2_v = obtener_precio_real(ccaa_v, pob_v, bar_v, mi_api, True)
            v_total = p_m2_v * m2_v
            
            # Gastos de salida
            gasto_inmo = v_total * (comision_inmo / 100)
            
            # Estimación Plusvalía Municipal (Simplificada según años)
            anos_propiedad = date.today().year - fecha_compra.year
            plusvalia_estimada = (v_total * 0.03) if anos_propiedad > 1 else 0 # Estimación conservadora
            
            neto_tras_venta = v_total - gasto_inmo - plusvalia_estimada - 1500 # 1500€ Notaría/Cancelación
            
            # 2. Análisis de Compra
            itp_compra = itp_dict[ccaa_c]
            gastos_fijos_compra = 0.015 # 1.5% para Notaría, Registro y Gestoría
            
            # Presupuesto real disponible para el inmueble (descontando impuestos y gastos)
            precio_max_inmueble = neto_tras_venta / (1 + itp_compra + gastos_fijos_compra)
            impuestos_pago = precio_max_inmueble * itp_compra
            gastos_pago = precio_max_inmueble * gastos_fijos_compra

            # --- RESULTADOS ---
            st.success(f"### Resultado del Análisis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Venta estimada en", f"{v_total:,.0f} €")
                st.write(f"**Gastos de venta:** {gasto_inmo + plusvalia_estimada + 1500:,.0f} €")
                st.write(f"(Inmo, Plusvalía, Notaría)")
            
            with col2:
                st.metric("Neto Líquido", f"{neto_tras_venta:,.0f} €")
                st.write("**Dinero real en tu bolsillo** tras vender y pagar todo.")

            st.divider()
            
            st.subheader(f"🏠 Tu capacidad de compra en {pob_c}")
            st.info(f"Puedes comprar un piso de hasta **{precio_max_inmueble:,.0f} €**")
            
            st.write(f"* **Impuesto (ITP {ccaa_c}):** {impuestos_pago:,.0f} €")
            st.write(f"* **Notaría y Registro:** {gastos_pago:,.0f} €")
            st.write(f"**Total Inversión:** {neto_tras_venta:,.0f} €")
