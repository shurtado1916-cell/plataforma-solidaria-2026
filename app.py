import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Causa Solidaria - Transparencia 2026",
    page_icon="🤝",
    layout="wide"
)

SHEET_ID = "10q-xB5QuLNAEu-0pkMPBHUGaD8JicnjAVYp_0YaC4ZY"

URL_INGRESOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Ingresos"
URL_EGRESOS = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Egresos"

st.markdown("""
    <style>
    .main { background-color: #F8F9FA; }
    div[data-testid="stMetric"] {
        background-color: #FFFFFF;
        padding: 15px 20px;
        border-radius: 10px;
        border-left: 5px solid #006B3F;
        box-shadow: 0px 2px 5px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def cargar_datos():
    try:
        df_ingresos = pd.read_csv(URL_INGRESOS)
        df_egresos = pd.read_csv(URL_EGRESOS)
        
        df_ingresos.columns = df_ingresos.columns.str.strip()
        df_egresos.columns = df_egresos.columns.str.strip()

        if 'Monto' in df_ingresos.columns:
            df_ingresos['Monto'] = pd.to_numeric(df_ingresos['Monto'], errors='coerce').fillna(0)
        if 'Monto' in df_egresos.columns:
            df_egresos['Monto'] = pd.to_numeric(df_egresos['Monto'], errors='coerce').fillna(0)
        
        return df_ingresos, df_egresos
    except Exception as e:
        return pd.DataFrame(), pd.DataFrame()

df_ingresos, df_egresos = cargar_datos()

st.title("🤝 Plataforma de Transparencia Solidaria")
st.markdown("**Transparencia y claridad total:** Uniendo esfuerzos para ayudar a 1 familia por mes de aquí a diciembre.")
st.divider()

META_MENSUAL = 1000000
col_mes_ingresos = next((col for col in ['Mes_Aplicado', 'Mes', 'Mes Aplicado', 'MES'] if col in df_ingresos.columns), None)

total_recaudado = df_ingresos['Monto'].sum() if 'Monto' in df_ingresos.columns else 0
familias_impactadas = len(df_egresos[df_egresos.get('Estado') == 'Entregado']) if not df_egresos.empty and 'Estado' in df_egresos.columns else 0

if col_mes_ingresos and 'Monto' in df_ingresos.columns:
    ingresos_agosto = df_ingresos[df_ingresos[col_mes_ingresos].astype(str).str.contains('Agosto', case=False, na=False)]['Monto'].sum()
else:
    ingresos_agosto = total_recaudado

porcentaje_mes = min(ingresos_agosto / META_MENSUAL, 1.0) if META_MENSUAL > 0 else 0.0

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="Meta Mes Actual (Agosto)", value=f"${META_MENSUAL:,.0f}", delta="Objetivo")

with col2:
    st.metric(label="Recaudado Este Mes", value=f"${ingresos_agosto:,.0f}", delta=f"{porcentaje_mes * 100:.1f}% alcanzado")

with col3:
    st.metric(label="Familias Impactadas", value=f"{familias_impactadas} de 5", delta="Meta: Diciembre")

st.write("**Progreso de recaudación del mes:**")
st.progress(porcentaje_mes)

st.divider()

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
        col_donante = next((col for col in ['Donante', 'Nombre', 'Aportante'] if col in df_filtrado.columns), None)
        
        if busqueda and col_donante:
            df_filtrado = df_filtrado[df_filtrado[col_donante].astype(str).str.contains(busqueda, case=False, na=False)]
        
        df_display = df_filtrado.copy()
        if 'Monto' in df_display.columns:
            df_display['Monto'] = df_display['Monto'].apply(lambda x: f"${x:,.0f}")
        st.dataframe(df_display, use_container_width=True)
    else:
        st.info("No hay datos registrados en la hoja de Ingresos aún.")

with tab_balance:
    st.subheader("Comparativo de Ingresos por Mes")
    if not df_ingresos.empty and col_mes_ingresos and 'Monto' in df_ingresos.columns:
        balance_mes = df_ingresos.groupby(col_mes_ingresos)['Monto'].sum().reset_index()
        
        fig = px.bar(
            balance_mes, 
            x=col_mes_ingresos, 
            y='Monto',
            text_auto='$,.0f',
            color_discrete_sequence=['#006B3F']
        )
        
        fig.update_traces(
            textposition='outside',
            textfont_size=14
        )
        
        fig.update_layout(
            xaxis_title="Mes",
            yaxis_title="Total Recaudado ($)",
            plot_bgcolor='rgba(0,0,0,0)',
            yaxis=dict(range=[0, balance_mes['Monto'].max() * 1.25])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay suficientes datos para generar gráficos de balance.")

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
