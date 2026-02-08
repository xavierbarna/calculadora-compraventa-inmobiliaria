import streamlit as st
import google.generativeai as genai

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="InmoReal AI", page_icon="💰")

# ITP por Comunidades
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
    tipo = "VENTA (PRECIO DE CIERRE)" if es_venta else "COMPRA (PRECIO DE CIERRE)"
    prompt = f"Precio medio m2 de {tipo} en {barrio}, {poblacion} ({comunidad}). Ignora precios de portales, dame precio de NOTARÍA. Responde SOLO el número."
    try:
        response = model.generate_content(prompt)
        return float(''.join(filter(lambda x: x.isdigit() or x == '.', response.text)))
    except:
        return 2500.0

# --- INTERFAZ ---
st.title("💰 Estrategia de Inversión Inmobiliaria")
st.markdown("Vende en zona cara, compra en zona barata y calcula tu ahorro.")

with st.sidebar:
    mi_api = st.text_input("Tu API Key de Google", type="password")
    st.divider()
    st.header("📍 Ubicación Venta")
    ccaa_v = st.selectbox("CCAA Venta", list(itp_dict.keys()))
    pob_v = st.text_input("Población Venta", "Madrid")
    bar_v = st.text_input("Barrio Venta", "Salamanca")
    m2_v = st.number_input("M2 de tu piso", value=80)

    st.header("📍 Ubicación Compra")
    ccaa_c = st.selectbox("CCAA Compra", list(itp_dict.keys()))
    pob_c = st.text_input("Población Compra", "Alicante")
    bar_c = st.text_input("Barrio Compra", "Centro")
    
    st.header("📈 Reinversión")
    pct_reinv = st.slider("% del neto que usarás para comprar", 0, 100, 70)

if st.button("EJECUTAR ANÁLISIS"):
    if not mi_api:
        st.error("Introduce tu API Key en la barra lateral.")
    else:
        with st.spinner('Calculando...'):
            # Lógica Venta
            p_m2_v = obtener_precio_real(ccaa_v, pob_v, bar_v, mi_api, True)
            v_total = p_m2_v * m2_v
            plusvalia = v_total * 0.03
            neto_venta = v_total - plusvalia
            
            # Lógica Compra y Ahorro
            presupuesto_total = neto_venta * (pct_reinv / 100)
            ahorro_caja = neto_venta - presupuesto_total
            
            tasa_itp = itp_dict[ccaa_c]
            precio_max_piso = presupuesto_total / (1 + tasa_itp)
            impuesto_itp = precio_max_piso * tasa_itp

            # Mostrar resultados
            st.divider()
            c1, c2, c3 = st.columns(3)
            c1.metric("Neto de tu Venta", f"{neto_venta:,.0f} €")
            c2.metric("Para comprar (con ITP)", f"{presupuesto_total:,.0f} €")
            c3.metric("EFECTIVO QUE TE SOBRA", f"{ahorro_caja:,.0f} €", delta="¡Ahorro!")

            st.write(f"---")
            st.success(f"🏠 Con tu presupuesto, puedes buscar un piso de hasta **{precio_max_piso:,.0f} €** (reservando {impuesto_itp:,.0f} € para el ITP de {ccaa_c}).")
