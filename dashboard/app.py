import streamlit as st
import pandas as pd
from pymongo import MongoClient
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import time
from datetime import datetime

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FraudTrix Elite v3.0",
    layout="wide",
    page_icon="🛡️",
    initial_sidebar_state="expanded"
)

# ─── THEME & CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Exo+2:wght@300;400;600;700&display=swap');

/* ── Global reset ── */
html, body, [class*="css"] {
    font-family: 'Exo 2', sans-serif;
    background-color: #060b14 !important;
    color: #c9d1d9 !important;
}

/* ── Animated gradient background ── */
.stApp {
    background: radial-gradient(ellipse at 20% 50%, rgba(0, 212, 255, 0.04) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 20%, rgba(255, 0, 110, 0.04) 0%, transparent 60%),
                #060b14;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1117 0%, #0a0f1a 100%) !important;
    border-right: 1px solid rgba(0, 212, 255, 0.15) !important;
}
section[data-testid="stSidebar"] * { color: #8b949e !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #00d4ff !important; }

/* ── KPI cards ── */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 12px;
    padding: 20px !important;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s ease, box-shadow 0.3s ease;
}
div[data-testid="stMetric"]:hover {
    border-color: rgba(0, 212, 255, 0.6);
    box-shadow: 0 0 20px rgba(0, 212, 255, 0.15);
}
div[data-testid="stMetric"]::before {
    content: "";
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00d4ff, #ff006e);
    opacity: 0.6;
}
div[data-testid="stMetric"] label {
    color: #6e7681 !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: 1.5px !important;
    font-family: 'Share Tech Mono', monospace !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #00d4ff !important;
    font-size: 28px !important;
    font-weight: 700 !important;
    font-family: 'Exo 2', sans-serif !important;
}
div[data-testid="stMetric"] [data-testid="stMetricDelta"] { font-size: 12px !important; }

/* ── Section headers ── */
.section-header {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #00d4ff;
    border-bottom: 1px solid rgba(0, 212, 255, 0.2);
    padding-bottom: 8px;
    margin-bottom: 16px;
    opacity: 0.8;
}

/* ── Chart containers ── */
.chart-container {
    background: linear-gradient(135deg, #0d1117 0%, #161b22 100%);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 16px;
    margin-bottom: 16px;
}

/* ── Alert badges ── */
.badge-fraud {
    background: rgba(255, 0, 110, 0.15);
    border: 1px solid rgba(255, 0, 110, 0.4);
    color: #ff006e;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 11px;
    font-family: 'Share Tech Mono', monospace;
    font-weight: 600;
}
.badge-safe {
    background: rgba(0, 204, 150, 0.1);
    border: 1px solid rgba(0, 204, 150, 0.3);
    color: #00cc96;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 11px;
    font-family: 'Share Tech Mono', monospace;
}

/* ── Status bar ── */
.status-bar {
    font-family: 'Share Tech Mono', monospace;
    font-size: 11px;
    color: #3fb950;
    background: rgba(63, 185, 80, 0.05);
    border: 1px solid rgba(63, 185, 80, 0.2);
    border-radius: 6px;
    padding: 6px 12px;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* ── Dataframe overrides ── */
div[data-testid="stDataFrame"] {
    border: 1px solid rgba(0, 212, 255, 0.1);
    border-radius: 10px;
    overflow: hidden;
}

/* ── Slider & toggle ── */
div[data-testid="stSlider"] > div > div > div { background: #00d4ff !important; }

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: #0d1117; }
::-webkit-scrollbar-thumb { background: rgba(0, 212, 255, 0.3); border-radius: 4px; }

/* ── Divider ── */
hr { border-color: rgba(0, 212, 255, 0.1) !important; }
</style>
""", unsafe_allow_html=True)

# ─── PLOTLY DARK TEMPLATE ──────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Exo 2, sans-serif", color="#8b949e", size=11),
    margin=dict(l=10, r=10, t=30, b=10),
    colorway=["#00d4ff", "#ff006e", "#3fb950", "#ff9f00", "#a78bfa"],
    xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
    yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)"),
)
FRAUD_COLORS = {True: "#ff006e", False: "#00d4ff", "True": "#ff006e", "False": "#00d4ff", 1: "#ff006e", 0: "#00d4ff"}

# ─── DB CONNECTION ─────────────────────────────────────────────────────────────
@st.cache_resource
def get_db():
    return MongoClient(os.getenv("MONGO_URI", "mongodb://mongodb:27017")).fraud_db

db = get_db()

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛡️ FraudTrix Elite")
    st.markdown('<p style="font-family: Share Tech Mono, monospace; font-size:10px; color:#6e7681; letter-spacing:2px;">REAL-TIME THREAT INTELLIGENCE</p>', unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### ⚙️ Filters")
    min_amt = st.slider("Min Transaction Amount ($)", 0, 12000, 0, step=100)
    max_amt = st.slider("Max Transaction Amount ($)", 0, 12000, 12000, step=100)
    show_only_fraud = st.toggle("🔴 High Risk Only", False)
    
    st.markdown("---")
    st.markdown("### 🗺️ Region Focus")
    all_cities = ["All", "Mumbai", "Nagpur", "New York", "London", "Dubai"]
    selected_city = st.selectbox("City", all_cities)

    st.markdown("---")
    st.markdown("### 📊 Display")
    record_limit = st.select_slider("Records to Display", [25, 50, 100, 200, 500], value=100)
    refresh_rate = st.select_slider("Refresh Rate (sec)", [1, 2, 5, 10], value=2)

    st.markdown("---")
    st.markdown(
        '<div class="status-bar">● LIVE  &nbsp; Stream Active</div>',
        unsafe_allow_html=True
    )

# ─── MAIN HEADER ──────────────────────────────────────────────────────────────
col_title, col_time = st.columns([3, 1])
with col_title:
    st.markdown(
        '<h1 style="font-family: Exo 2, sans-serif; font-weight:700; font-size:28px; '
        'background: linear-gradient(90deg, #00d4ff, #ff006e); -webkit-background-clip: text; '
        '-webkit-text-fill-color: transparent; margin-bottom:0;">🛡️ FraudTrix Elite v3.0</h1>',
        unsafe_allow_html=True
    )
    st.markdown(
        '<p style="font-family: Share Tech Mono, monospace; font-size:11px; color:#6e7681; '
        'letter-spacing:2px; margin-top:2px;">ADVANCED FRAUD DETECTION & INTELLIGENCE PLATFORM</p>',
        unsafe_allow_html=True
    )
with col_time:
    time_display = st.empty()

# ─── MAIN REFRESH LOOP ────────────────────────────────────────────────────────
placeholder = st.empty()

while True:
    time_display.markdown(
        f'<div style="text-align:right; font-family: Share Tech Mono, monospace; '
        f'font-size:11px; color:#6e7681; padding-top:12px;">'
        f'🕐 {datetime.now().strftime("%H:%M:%S")}</div>',
        unsafe_allow_html=True
    )

    with placeholder.container():
        # ── Build query ──
        query = {"amount": {"$gte": min_amt, "$lte": max_amt}}
        if show_only_fraud:
            query["is_fraud"] = True
        if selected_city != "All":
            query["city"] = selected_city

        raw_data = list(db.transactions.find(query).sort("_id", -1).limit(record_limit))

        if not raw_data:
            st.info("📡 Awaiting transaction stream… Ensure the producer service is running.")
        else:
            df = pd.DataFrame(raw_data)
            df["is_fraud"] = df["is_fraud"].astype(bool)

            total     = db.transactions.count_documents({})
            frauds    = db.transactions.count_documents({"is_fraud": True})
            fraud_rate = (frauds / total * 100) if total > 0 else 0
            avg_risk   = df["risk_score"].mean()
            high_risk  = int((df["risk_score"] >= 75).sum())

            # ── KPI Row ──────────────────────────────────────────────────────
            st.markdown('<p class="section-header">// GLOBAL PERFORMANCE INDICATORS</p>', unsafe_allow_html=True)
            k1, k2, k3, k4, k5 = st.columns(5)
            k1.metric("Total Transactions", f"{total:,}")
            k2.metric("Fraud Rate", f"{fraud_rate:.2f}%", delta=f"{frauds} flagged", delta_color="inverse")
            k3.metric("Avg Risk Score", f"{avg_risk:.1f}/100")
            k4.metric("High Risk (batch)", str(high_risk), delta_color="inverse")
            k5.metric("Active Regions", str(df["city"].nunique()))

            st.markdown("---")

            # ── Row 1: Map + Donut ────────────────────────────────────────────
            st.markdown('<p class="section-header">// SPATIAL INTELLIGENCE & THREAT DISTRIBUTION</p>', unsafe_allow_html=True)
            r1c1, r1c2 = st.columns([3, 1])

            with r1c1:
                fig_map = px.scatter_mapbox(
                    df, lat="lat", lon="lon",
                    color=df["is_fraud"].map({True: "HIGH RISK", False: "SAFE"}),
                    size="amount",
                    hover_name="city",
                    hover_data={"risk_score": True, "amount": True, "type": True, "device": True, "lat": False, "lon": False},
                    zoom=1, height=400,
                    color_discrete_map={"HIGH RISK": "#ff006e", "SAFE": "#00d4ff"},
                    mapbox_style="carto-darkmatter",
                    title="Live Transaction Geospatial Feed"
                )
                fig_map.update_layout(
                    **CHART_LAYOUT,
                    height=400,
                    legend=dict(orientation="h", yanchor="bottom", y=1, xanchor="right", x=1,
                                font=dict(size=10), bgcolor="rgba(0,0,0,0.5)")
                )
                st.plotly_chart(fig_map, use_container_width=True)

            with r1c2:
                # Donut: fraud vs legit
                labels = ["Legitimate", "High Risk"]
                values = [total - frauds, frauds]
                fig_donut = go.Figure(go.Pie(
                    labels=labels, values=values, hole=0.65,
                    marker=dict(colors=["#00d4ff", "#ff006e"],
                                line=dict(color="#060b14", width=3)),
                    textfont=dict(family="Exo 2"),
                    hovertemplate="%{label}: %{value}<extra></extra>"
                ))
                fig_donut.add_annotation(
                    text=f"<b>{fraud_rate:.1f}%</b><br><span style='font-size:10px'>FRAUD</span>",
                    x=0.5, y=0.5, showarrow=False,
                    font=dict(size=18, color="#ff006e", family="Exo 2")
                )
                fig_donut.update_layout(**CHART_LAYOUT, height=400, title="Fraud Ratio",
                                        showlegend=True,
                                        legend=dict(orientation="h", y=-0.1))
                st.plotly_chart(fig_donut, use_container_width=True)

            # ── Row 2: Risk histogram + Device sunburst + Type grouped bar ────
            st.markdown('<p class="section-header">// BEHAVIORAL & DEVICE ANALYSIS</p>', unsafe_allow_html=True)
            r2c1, r2c2, r2c3 = st.columns(3)

            with r2c1:
                fig_hist = px.histogram(
                    df, x="risk_score", nbins=20,
                    color=df["is_fraud"].map({True: "HIGH RISK", False: "SAFE"}),
                    color_discrete_map={"HIGH RISK": "#ff006e", "SAFE": "#00d4ff"},
                    barmode="overlay", opacity=0.8,
                    title="Risk Score Distribution"
                )
                fig_hist.add_vline(x=75, line_dash="dash", line_color="#ff9f00",
                                   annotation_text="Threshold", annotation_font_color="#ff9f00")
                fig_hist.update_layout(**CHART_LAYOUT, height=320)
                st.plotly_chart(fig_hist, use_container_width=True)

            with r2c2:
                fig_sunburst = px.sunburst(
                    df,
                    path=["device", df["is_fraud"].map({True: "HIGH RISK", False: "SAFE"})],
                    values="amount",
                    color=df["is_fraud"].map({True: "HIGH RISK", False: "SAFE"}),
                    color_discrete_map={"HIGH RISK": "#ff006e", "SAFE": "#00d4ff"},
                    title="Device Risk Profile"
                )
                fig_sunburst.update_traces(textfont=dict(family="Exo 2"))
                fig_sunburst.update_layout(**CHART_LAYOUT, height=320)
                st.plotly_chart(fig_sunburst, use_container_width=True)

            with r2c3:
                fig_bar = px.bar(
                    df, x="type", y="amount",
                    color=df["is_fraud"].map({True: "HIGH RISK", False: "SAFE"}),
                    color_discrete_map={"HIGH RISK": "#ff006e", "SAFE": "#00d4ff"},
                    barmode="group",
                    title="Transaction Type Breakdown"
                )
                fig_bar.update_layout(**CHART_LAYOUT, height=320)
                st.plotly_chart(fig_bar, use_container_width=True)

            # ── Row 3: Scatter + City heatbar ─────────────────────────────────
            st.markdown('<p class="section-header">AMOUNT vs RISK CORRELATION & CITY EXPOSURE</p>', unsafe_allow_html=True)
            r3c1, r3c2 = st.columns([2, 1])

            with r3c1:
                fig_scatter = px.scatter(
                    df, x="amount", y="risk_score",
                    color=df["is_fraud"].map({True: "HIGH RISK", False: "SAFE"}),
                    size="amount", hover_name="city",
                    hover_data={"type": True, "device": True},
                    color_discrete_map={"HIGH RISK": "#ff006e", "SAFE": "#00d4ff"},
                    trendline="ols",
                    title="Risk Score vs Transaction Amount (OLS Trendline)"
                )
                fig_scatter.update_layout(**CHART_LAYOUT, height=320)
                st.plotly_chart(fig_scatter, use_container_width=True)

            with r3c2:
                city_risk = (
                    df.groupby("city")
                    .agg(avg_risk=("risk_score", "mean"), count=("id", "count"))
                    .reset_index()
                    .sort_values("avg_risk", ascending=True)
                )
                fig_city = go.Figure(go.Bar(
                    y=city_risk["city"], x=city_risk["avg_risk"],
                    orientation="h",
                    marker=dict(
                        color=city_risk["avg_risk"],
                        colorscale=[[0, "#00d4ff"], [0.5, "#ff9f00"], [1, "#ff006e"]],
                        showscale=False
                    ),
                    text=city_risk["avg_risk"].round(1),
                    textposition="outside",
                    hovertemplate="<b>%{y}</b><br>Avg Risk: %{x:.1f}<extra></extra>"
                ))
                fig_city.update_layout(**CHART_LAYOUT, height=320, title="City Risk Exposure")
                st.plotly_chart(fig_city, use_container_width=True)

            # ── Row 4: Time series of amounts ─────────────────────────────────
            if "timestamp" in df.columns:
                st.markdown('<p class="section-header">TRANSACTION VOLUME TIMELINE</p>', unsafe_allow_html=True)
                df_time = df.copy()
                df_time["time"] = pd.to_datetime(df_time["timestamp"], unit="s")
                df_time = df_time.sort_values("time")

                fig_line = px.area(
                    df_time, x="time", y="amount",
                    color=df_time["is_fraud"].map({True: "HIGH RISK", False: "SAFE"}),
                    color_discrete_map={"HIGH RISK": "#ff006e", "SAFE": "#00d4ff"},
                    title="Transaction Amount Over Time",
                    line_group=df_time["is_fraud"].map({True: "HIGH RISK", False: "SAFE"})
                )
                fig_line.update_traces(opacity=0.6)
                fig_line.update_layout(**CHART_LAYOUT, height=250)
                st.plotly_chart(fig_line, use_container_width=True)

            # ── Audit Log ─────────────────────────────────────────────────────
            st.markdown('<p class="section-header">// REAL-TIME AUDIT LOG</p>', unsafe_allow_html=True)

            display_cols = [c for c in ["id", "amount", "type", "city", "device", "risk_score", "is_fraud"] if c in df.columns]
            df_display = df[display_cols].copy()
            df_display["is_fraud"] = df_display["is_fraud"].map({True: "🔴 HIGH RISK", False: "🟢 SAFE"})

            def _style_row(row):
                if "🔴" in str(row.get("is_fraud", "")):
                    return ["background-color: rgba(255,0,110,0.05)" for _ in row]
                return ["" for _ in row]

            styled = (
                df_display.style
                .apply(_style_row, axis=1)
                .background_gradient(cmap="RdYlGn_r", subset=["risk_score"] if "risk_score" in display_cols else [])
                .format({"amount": "${:,.2f}", "risk_score": "{:.0f}"})
            )
            st.dataframe(styled, use_container_width=True, height=350)

            # ── Footer ────────────────────────────────────────────────────────
            st.markdown(
                '<hr><p style="font-family: Share Tech Mono, monospace; font-size:10px; '
                'color:#3d444d; text-align:center;">FraudTrix Elite v3.0 — '
                'Powered by Apache Kafka · MongoDB · Streamlit — '
                f'Last refresh: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>',
                unsafe_allow_html=True
            )

    time.sleep(refresh_rate)