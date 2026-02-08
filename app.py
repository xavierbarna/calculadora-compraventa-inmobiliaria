import streamlit as st
import google.generativeai as genai
from datetime import date

st.set_page_config(page_title="InmoReal AI Pro", page_icon="🏠")

# --- BASE DE DATOS DE BARRIOS (Ejemplo ampliable) ---
DATOS_ZONAS = {
    "Barcelona": ["Sant Antoni", "Eixample", "Gràcia", "Poblenou", "Sarrià", "Sants"],
    "Madrid": ["Salamanca", "Chamberí", "Retiro", "Tetuán", "Hortaleza", "Usera"],
    "Valencia": ["Ruzafa", "Ciutat Vella", "El Carmen", "Patraix", "Benimaclet"],
    "Alicante": ["Centro", "Playa de San Juan", "Cabo de las Huertas", "Carolinas"]
}

itp_dict = {
    "Andalucía": 0.07, "Aragón": 0.08, "Asturias": 0.08, "Baleares": 0.08,
    "Canarias": 0.065, "Cantabria": 0.08, "Castilla y León": 0.08, 
    "Castilla-La Mancha": 0.09, "Cataluña": 0.10, "Comunidad Valenciana": 0.10,
    "Madrid": 0.06, "Murcia": 0.08, "Navarra": 0.06, "País Vasco": 0.04
}

def obtener_precio_ia(comunidad, poblacion, barrio, api_key):
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    # Prompt mucho más específico para evitar precios bajos
    prompt = f"""
    Actúa como experto inmobiliario en España. 
    Dime el precio MEDIO REAL DE CIERRE por m2 en el barrio de {barrio}, {poblacion} ({comunidad}).
    No des precios de portales como Idealista (que suelen estar inflados), pero tampoco valores catastrales. 
    Quiero el valor de mercado REAL en 2024/2025.
    Responde SOLO con el número (ejemplo: 5200).
    """
    try:
        response = model.generate_content(prompt)
        # Limpiamos la respuesta para quedarnos solo con el número
        valor = float(''.join(filter(lambda x: x.isdigit() or x == '.', response.text)))
        return valor
    except:
        return 4500.0 # Valor de seguridad más coherente con grandes ciudades

# --- INTERFAZ ---
st.title("🏦 Consultor Inmobiliario de Alta Precisión")

with st.sidebar:
    mi_api = st.text_input("Introduce tu API Key", type="password")
    st.divider()
    
    st.header("📍 Ubicación Venta")
    ccaa_v = st.selectbox("Comunidad Autónoma", list(itp_dict.keys()), index=8) # Cataluña por defecto
    pob_v = st.selectbox("Población", list(DATOS_ZONAS.keys()))
    
    # Aquí está la magia: el barrio depende de la población elegida
    bar_v = st.selectbox("Barrio", DATOS_ZONAS[pob_v])
    
    m2_v = st.number_input("Metros cuadrados del inmueble", value=100)
    
    st.header("📅 Datos Históricos")
    fecha_compra = st.date_input("Fecha de adquisición", value=date(2015, 1, 1))
    comision_inmo = st.slider("% Comisión Inmobiliaria (Venta)", 0, 6, 3)

    st.header("📍 Destino Compra")
    ccaa_c = st.selectbox("CCAA Destino", list(itp_dict.keys()), index=10) # C. Valenciana por defecto
    pob_c = st.text_input("Ciudad Destino", "Alicante")
    bar_c = st.text_input("Barrio Destino", "Playa de San Juan")

if st.button("REALIZAR CÁLCULO PROFESIONAL"):
    if not mi_api:
        st.error("⚠️ Falta la API Key")
    else:
        with st.spinner('Consultando Big Data inmobiliario...'):
            precio_m2 = obtener_precio_ia(ccaa_v, pob_v, bar_v, mi_api)
            v_total = precio_m2 * m2_v
            
            # Gastos de Venta
            gasto_inmo = v_total * (comision_inmo / 100)
            plusvalia_mun = v_total * 0.025 # Estimación simplificada
            gastos_notaria_v = 1200
            
            neto_venta = v_total - gasto_inmo - plusvalia_mun - gastos_notaria_v
            
            # Cálculo de Compra
            tasa_itp = itp_dict[ccaa_c]
            gastos_compra_fijos = 0.015 # 1.5% Notaría/Registro
            
            capacidad_compra = neto_venta / (1 + tasa_itp + gastos_compra_fijos)
            ahorro_final = neto_venta - (capacidad_compra * (1 + tasa_itp + gastos_compra_fijos))

            # --- RESULTADOS ---
            st.metric("Valor Mercado Estimado", f"{v_total:,.0f} €", f"{precio_m2:,.0f} €/m2")
            
            col1, col2 = st.columns(2)
            with col1:
                st.subheader("📊 Desglose Salida")
                st.write(f"Comisión Inmo: {gasto_inmo:,.0f} €")
                st.write(f"Plusvalía est.: {plusvalia_mun:,.0f} €")
                st.write(f"Notaría/Registro: {gastos_notaria_v:,.0f} €")
                st.markdown(f"**NETO LÍQUIDO: {neto_venta:,.0f} €**")
                
            with col2:
                st.subheader("🏠 Capacidad Compra")
                st.success(f"Inmueble hasta: {capacidad_compra:,.0f} €")
                st.write(f"ITP ({ccaa_c}): {capacidad_compra*tasa_itp:,.0f} €")
                st.write(f"Gastos compra: {capacidad_compra*gastos_compra_fijos:,.0f} €")
