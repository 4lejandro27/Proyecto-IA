"""
ServiceBot Dashboard - Panel Administrativo
Ejecutar con: streamlit run dashboard.py
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import json
import os

# Configuracion de pagina
st.set_page_config(
    page_title="ServiceBot Dashboard",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    .status-pendiente { color: #f0ad4e; font-weight: bold; }
    .status-completado { color: #5cb85c; font-weight: bold; }
    .status-urgente { color: #d9534f; font-weight: bold; }
    .lead-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sidebar-logo {
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem 0;
        border-bottom: 2px solid #eee;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Datos de ejemplo (en produccion vendrian de la base de datos)
sample_leads = [
    {
        "fecha": "2026-07-22", "hora": "09:15:30", "nombre": "Carlos Rodriguez",
        "telefono": "+5215512345678", "email": "carlos@email.com",
        "ciudad": "Ciudad de Mexico", "direccion": "Av. Insurgentes 1234, Col. Roma",
        "tipo_servicio": "plomeria", "problema": "Tuberia rota en bano principal",
        "urgencia": "alta", "horario": "manana", "precio_estimado": "$50 - $150 (tarifa de emergencia puede aplicar)",
        "estado": "pendiente", "canal": "whatsapp", "origen": "organico", "notas": ""
    },
    {
        "fecha": "2026-07-22", "hora": "08:45:12", "nombre": "Maria Gonzalez",
        "telefono": "+5215587654321", "email": "maria.g@email.com",
        "ciudad": "Guadalajara", "direccion": "Calle Hidalgo 567, Centro",
        "tipo_servicio": "electricidad", "problema": "Se fue la luz en toda la casa",
        "urgencia": "alta", "horario": "tarde", "precio_estimado": "$40 - $120",
        "estado": "pendiente", "canal": "whatsapp", "origen": "organico", "notas": ""
    },
    {
        "fecha": "2026-07-21", "hora": "16:20:45", "nombre": "Juan Perez",
        "telefono": "+5215532145678", "email": "juan.p@email.com",
        "ciudad": "Monterrey", "direccion": "Av. Constitucion 890, Col. Obispado",
        "tipo_servicio": "aire_acondicionado", "problema": "El aire no enfria, solo ventila",
        "urgencia": "media", "horario": "manana", "precio_estimado": "$60 - $200",
        "estado": "completado", "canal": "whatsapp", "origen": "organico", "notas": "Tecnico asignado: Roberto"
    },
    {
        "fecha": "2026-07-21", "hora": "11:10:22", "nombre": "Ana Martinez",
        "telefono": "+5215567890123", "email": "ana.m@email.com",
        "ciudad": "Puebla", "direccion": "Calle 5 de Mayo 234, Centro",
        "tipo_servicio": "limpieza", "problema": "Limpieza profunda de oficina de 200m2",
        "urgencia": "baja", "horario": "tarde", "precio_estimado": "$40 - $150",
        "estado": "pendiente", "canal": "whatsapp", "origen": "organico", "notas": ""
    },
    {
        "fecha": "2026-07-20", "hora": "14:30:00", "nombre": "Luis Hernandez",
        "telefono": "+5215543216789", "email": "luis.h@email.com",
        "ciudad": "Ciudad de Mexico", "direccion": "Av. Reforma 1000, Col. Juarez",
        "tipo_servicio": "cerrajeria", "problema": "Se quedo encerrado, cerradura danada",
        "urgencia": "alta", "horario": "noche", "precio_estimado": "$30 - $100 (tarifa de emergencia puede aplicar)",
        "estado": "completado", "canal": "whatsapp", "origen": "organico", "notas": "Resuelto en 20 min"
    },
]

# Convertir a DataFrame
df = pd.DataFrame(sample_leads)

# Sidebar
st.sidebar.markdown('<div class="sidebar-logo">🔧 ServiceBot</div>', unsafe_allow_html=True)
st.sidebar.markdown("---")

# Menu de navegacion
menu = st.sidebar.radio(
    "Navegacion",
    ["📊 Dashboard", "📋 Leads", "📈 Analiticas", "⚙️ Configuracion"]
)

st.sidebar.markdown("---")
st.sidebar.info("""
**ServiceBot v1.0**
Asistente virtual inteligente para negocios de servicios.

📞 WhatsApp API activo
🤖 OpenAI GPT-4o-mini
📊 Google Sheets conectado
""")

# ==========================================
# PAGINA: DASHBOARD
# ==========================================
if menu == "📊 Dashboard":
    st.markdown('<div class="main-header">📊 Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Vista general de tu negocio</div>', unsafe_allow_html=True)

    # Metricas principales
    col1, col2, col3, col4 = st.columns(4)

    total_leads = len(df)
    pendientes = len(df[df['estado'] == 'pendiente'])
    completados = len(df[df['estado'] == 'completado'])
    urgentes = len(df[df['urgencia'] == 'alta'])

    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{total_leads}</div><div class="metric-label">Total Leads</div></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);"><div class="metric-value">{pendientes}</div><div class="metric-label">Pendientes</div></div>', unsafe_allow_html=True)

    with col3:
        st.markdown(f'<div class="metric-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);"><div class="metric-value">{completados}</div><div class="metric-label">Completados</div></div>', unsafe_allow_html=True)

    with col4:
        st.markdown(f'<div class="metric-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);"><div class="metric-value">{urgentes}</div><div class="metric-label">Urgentes</div></div>', unsafe_allow_html=True)

    st.markdown("---")

    # Graficos
    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📈 Leads por dia")
        leads_por_dia = df.groupby('fecha').size().reset_index(name='cantidad')
        st.bar_chart(leads_por_dia.set_index('fecha'))

    with col_right:
        st.subheader("🔧 Servicios mas solicitados")
        servicios = df['tipo_servicio'].value_counts()
        st.bar_chart(servicios)

    st.markdown("---")

    # Leads recientes
    st.subheader("🚨 Leads recientes (ultimas 24h)")
    recientes = df[df['fecha'] == '2026-07-22'].sort_values('hora', ascending=False)

    for _, lead in recientes.iterrows():
        emoji_urgencia = {"alta": "🔴", "media": "🟡", "baja": "🟢"}.get(lead['urgencia'], "⚪")
        emoji_estado = {"pendiente": "⏳", "completado": "✅"}.get(lead['estado'], "❓")

        st.markdown(f'<div class="lead-card"><b>{emoji_urgencia} {lead["nombre"]}</b> | {emoji_estado} <span class="status-{lead["estado"]}">{lead["estado"].upper()}</span> | 🔧 {lead["tipo_servicio"].upper()} | 📍 {lead["ciudad"]} | 💰 {lead["precio_estimado"]}<br><small>📝 {lead["problema"]} | 📞 {lead["telefono"]} | ⏰ {lead["hora"]}</small></div>', unsafe_allow_html=True)

# ==========================================
# PAGINA: LEADS
# ==========================================
elif menu == "📋 Leads":
    st.markdown('<div class="main-header">📋 Gestion de Leads</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Administra todas tus solicitudes</div>', unsafe_allow_html=True)

    # Filtros
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        filtro_estado = st.selectbox("Estado", ["Todos", "Pendiente", "Completado", "Cancelado"])
    with col2:
        filtro_urgencia = st.selectbox("Urgencia", ["Todos", "Alta", "Media", "Baja"])
    with col3:
        filtro_servicio = st.selectbox("Servicio", ["Todos"] + sorted(df['tipo_servicio'].unique().tolist()))
    with col4:
        filtro_ciudad = st.selectbox("Ciudad", ["Todos"] + sorted(df['ciudad'].unique().tolist()))

    # Aplicar filtros
    df_filtrado = df.copy()
    if filtro_estado != "Todos":
        df_filtrado = df_filtrado[df_filtrado['estado'] == filtro_estado.lower()]
    if filtro_urgencia != "Todos":
        df_filtrado = df_filtrado[df_filtrado['urgencia'] == filtro_urgencia.lower()]
    if filtro_servicio != "Todos":
        df_filtrado = df_filtrado[df_filtrado['tipo_servicio'] == filtro_servicio.lower()]
    if filtro_ciudad != "Todos":
        df_filtrado = df_filtrado[df_filtrado['ciudad'] == filtro_ciudad]

    st.markdown(f"**{len(df_filtrado)} leads encontrados**")

    # Tabla de leads
    st.dataframe(
        df_filtrado[["fecha", "hora", "nombre", "telefono", "tipo_servicio", "urgencia", "estado", "precio_estimado", "ciudad"]],
        use_container_width=True
    )

    # Detalle de lead seleccionado
    st.markdown("---")
    st.subheader("🔍 Detalle del Lead")

    if len(df_filtrado) > 0:
        lead_seleccionado = st.selectbox("Selecciona un lead", df_filtrado['nombre'].tolist())
        lead = df_filtrado[df_filtrado['nombre'] == lead_seleccionado].iloc[0]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**👤 Cliente:** {lead['nombre']}")
            st.markdown(f"**📞 Telefono:** {lead['telefono']}")
            st.markdown(f"**📧 Email:** {lead['email']}")
            st.markdown(f"**📍 Direccion:** {lead['direccion']}")
            st.markdown(f"**🏙️ Ciudad:** {lead['ciudad']}")
        with col2:
            st.markdown(f"**🔧 Servicio:** {lead['tipo_servicio'].upper()}")
            st.markdown(f"**🚨 Urgencia:** {lead['urgencia'].upper()}")
            st.markdown(f"**⏰ Horario:** {lead['horario']}")
            st.markdown(f"**💰 Precio Est.:** {lead['precio_estimado']}")
            st.markdown(f"**📊 Estado:** {lead['estado'].upper()}")

        st.markdown(f"**📝 Problema:** {lead['problema']}")
        st.markdown(f"**📅 Fecha/Hora:** {lead['fecha']} {lead['hora']}")

        # Acciones
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("✅ Marcar como Completado"):
                st.success("Lead marcado como completado!")
        with col2:
            if st.button("👤 Asignar Tecnico"):
                st.info("Funcion: Asignar tecnico")
        with col3:
            if st.button("📧 Enviar Email"):
                st.info("Funcion: Enviar email al cliente")

# ==========================================
# PAGINA: ANALITICAS
# ==========================================
elif menu == "📈 Analiticas":
    st.markdown('<div class="main-header">📈 Analiticas</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Metricas de rendimiento</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("📊 Conversion")
        tasa_conversion = (completados / total_leads * 100) if total_leads > 0 else 0
        st.metric("Tasa de Conversion", f"{tasa_conversion:.1f}%", "+5.2%")

    with col2:
        st.subheader("⏱️ Tiempo Promedio")
        st.metric("Tiempo de Respuesta", "3.2 min", "-0.8 min")

    with col3:
        st.subheader("💰 Ingresos Estimados")
        st.metric("Valor Total", "$2,450", "+$320")

    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📅 Leads por semana")
        semanas = pd.DataFrame({
            'Semana': ['Sem 1', 'Sem 2', 'Sem 3', 'Sem 4'],
            'Leads': [12, 18, 15, 22]
        })
        st.line_chart(semanas.set_index('Semana'))

    with col2:
        st.subheader("🌍 Distribucion por ciudad")
        ciudades = df['ciudad'].value_counts()
        st.bar_chart(ciudades)

    st.markdown("---")

    st.subheader("🔥 Embudo de Conversion")
    funnel_data = pd.DataFrame({
        'Etapa': ['Mensaje Recibido', 'Info Completa', 'Cotizacion Enviada', 'Servicio Agendado', 'Servicio Completado'],
        'Cantidad': [100, 85, 72, 58, 45]
    })
    st.bar_chart(funnel_data.set_index('Etapa'))

# ==========================================
# PAGINA: CONFIGURACION
# ==========================================
elif menu == "⚙️ Configuracion":
    st.markdown('<div class="main-header">⚙️ Configuracion</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Personaliza tu ServiceBot</div>', unsafe_allow_html=True)

    st.subheader("🏢 Informacion del Negocio")

    col1, col2 = st.columns(2)
    with col1:
        nombre_negocio = st.text_input("Nombre del negocio", "Servicios Express")
        telefono_negocio = st.text_input("Telefono de contacto", "+52 55 1234 5678")
    with col2:
        email_negocio = st.text_input("Email de contacto", "contacto@serviciosexpress.com")
        ciudad_negocio = st.text_input("Ciudad principal", "Ciudad de Mexico")

    st.markdown("---")
    st.subheader("🔧 Servicios Ofrecidos")

    servicios = st.multiselect(
        "Selecciona los servicios que ofreces",
        ["Plomeria", "Electricidad", "Aire Acondicionado", "Cerrajeria", 
         "Limpieza", "Mantenimiento", "Fumigacion", "Reparaciones"],
        default=["Plomeria", "Electricidad", "Aire Acondicionado", "Cerrajeria"]
    )

    st.markdown("---")
    st.subheader("💰 Precios Base")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.number_input("Plomeria - Minimo", value=50)
        st.number_input("Electricidad - Minimo", value=40)
    with col2:
        st.number_input("Aire Acondicionado - Minimo", value=60)
        st.number_input("Cerrajeria - Minimo", value=30)
    with col3:
        st.number_input("Limpieza - Minimo", value=40)
        st.number_input("Mantenimiento - Minimo", value=50)

    st.markdown("---")
    st.subheader("🤖 Configuracion de IA")

    tono_ia = st.selectbox("Tono del asistente", ["Profesional", "Amigable", "Formal", "Casual"])
    respuesta_rapida = st.checkbox("Respuestas rapidas (menos de 3 segundos)", value=True)
    cotizacion_auto = st.checkbox("Cotizacion automatica", value=True)

    st.markdown("---")

    if st.button("💾 Guardar Configuracion", type="primary"):
        st.success("✅ Configuracion guardada correctamente!")
        st.balloons()

# Footer
st.markdown("---")
st.caption("🔧 ServiceBot v1.0 | Desarrollado con ❤️ para negocios de servicios")
