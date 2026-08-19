import streamlit as st
import pandas as pd

# ---------------------------------------------------------
# CONFIGURACIÓN DE LA PÁGINA
# ---------------------------------------------------------
st.set_page_config(
    page_title="Causa Solidaria - Transparencia 2026",
    page_icon="🤝",
    layout="wide"
)

# REEMPLAZA ESTE TEXTO CON LA ID REAL DE TU GOOGLE SHEETS
SHEET_ID = "10q-xB5QuLNAEu-0pkMPBHUGaD8JicnjAVYp_0YaC4ZY"

# URLs para exportar pestañas directamente a formato CSV
URL_INGRESOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Ingresos"
URL_EGRESOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Egresos"

# Estilos personalizados (Gris neutro + Verde institucional)
st.markdown("""
    
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# CARGA Y PROCESAMIENTO DE DATOS
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def cargar_datos():
    try:
        df_ingresos = pd.read_csv(URL_INGRESOS)
        df_egresos = pd.read_csv(URL_EGRESOS)
        
        df_ingresos['Monto'] = pd.to_numeric(df_ingresos['Monto'], errors='coerce').fillna(0)
        df_egresos['Monto'] = pd.to_numeric(df_egresos['Monto'], errors='coerce').fillna(0)
        
        return df_ingresos, df_egresos
    except Exception as e:
        st.error(f"Error al conectar con Google Sheets: {e}")
        return pd.DataFrame(), pd.DataFrame()

df_ingresos, df_egresos = cargar_datos()

# ---------------------------------------------------------
# ENCABEZADO
# ---------------------------------------------------------
st.title("🤝 Plataforma de Transparencia Solidaria")
st.markdown("**Transparencia y claridad total:** Uniendo esfuerzos para ayudar a 1 familia por mes de aquí a diciembre.")
st.divider()

# ---------------------------------------------------------
# CÁLCULOS PRINCIPALES
# ---------------------------------------------------------
META_MENSUAL = 1000000

total_recaudado = df_ingresos['Monto'].sum() if not df_ingresos.empty else 0
familias_impactadas = len(df_egresos[df_egresos['Estado'] == 'Entregado']) if not df_egresos.empty else 0

ingresos_agosto = df_ingresos[df_ingresos['Mes_Aplicado'] == 'Agosto']['Monto'].sum() if not df_ingresos.empty else 0
porcentaje_mes = min(ingresos_agosto / META_MENSUAL, 1.0) if META_MENSUAL > 0 else 0.0

# ---------------------------------------------------------
# TARJETAS DE MÉTRICAS Y PROGRESO
# ---------------------------------------------------------
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="Meta Mes Actual (Agosto)", 
        value=f"${META_MENSUAL:,.0f}",
        delta="Objetivo"
    )

with col2:
    st.metric(
        label="Recaudado Este Mes", 
        value=f"${ingresos_agosto:,.0f}", 
        delta=f"{porcentaje_mes * 100:.1f}% alcanzado"
    )

with col3:
    st.metric(
        label="Familias Impactadas", 
        value=f"{familias_impactadas} de 5", 
        delta="Meta: Diciembre"
    )

st.write("**Progreso de recaudación del mes:**")
st.progress(porcentaje_mes)

st.divider()

# ---------------------------------------------------------
# PESTAÑAS DE DETALLE
# ---------------------------------------------------------
st.header("📋 Seguimiento de Fondos y Soportes")

tab_historial, tab_balance, tab_impacto = st.tabs([
    "👥 Aportes de Donantes", 
    "📊 Balance General", 
    "🏡 Historias e Impacto"
])

with tab_historial:
    st.subheader("Registro de Entradas")
    st.caption("Usa la barra de búsqueda para verificar el estado de tu aporte de manera transparente.")
    
    if not df_ingresos.empty:
        busqueda = st.text_input("🔍 Buscar donante por nombre o código:", "")
        df_filtrado = df_ingresos.copy()
        
        if busqueda:
            df_filtrado = df_filtrado[df_filtrado['Donante'].astype(str).str.contains(busqueda, case=False, na=False)]
        
        df_display = df_filtrado.copy()
        df_display['Monto'] = df_display['Monto'].apply(lambda x: f"${x:,.0f}")
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("No hay datos registrados en la hoja de Ingresos aún.")

with tab_balance:
    st.subheader("Comparativo de Ingresos por Mes")
    if not df_ingresos.empty:
        balance_mes = df_ingresos.groupby('Mes_Aplicado')['Monto'].sum().reset_index()
        st.bar_chart(balance_mes.set_index('Mes_Aplicado'))
    else:
        st.info("No hay suficientes datos para generar gráficos.")

with tab_impacto:
    st.subheader("Bitácora de Ayudas Entregadas")
    if not df_egresos.empty:
        cols = st.columns(2)
        for idx, row in df_egresos.iterrows():
            col_target = cols[idx % 2]
            with col_target:
                estado_color = "🟢" if row.get('Estado') == 'Entregado' else "🟠"
                st.markdown(f"### {estado_color} {row.get('Mes', 'Mes')} - {row.get('Familia', 'Familia')}")
                st.write(f"**Detalle:** {row.get('Detalle', 'N/A')}")
                st.write(f"**Monto Invertido:** ${row.get('Monto', 0):,.0f}")
                st.write(f"**Estado:** {row.get('Estado', 'Pendiente')}")
                
                link = row.get('Link_Soporte', '')
                if pd.notna(link) and str(link).startswith('http'):
                    st.link_button("📄 Ver Fotos y Facturas", link)
                st.divider()
    else:
        st.info("Aún no se han subido registros de egresos.")
