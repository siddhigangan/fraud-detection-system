import streamlit as st
import pandas as pd
from pymongo import MongoClient
import plotly.express as px
import os
import time

st.set_page_config(page_title="FraudTrix Elite v2.0", layout="wide", page_icon="🕵️")

# CSS for better UI
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True) # <-- Fixed argument name

db = MongoClient(os.getenv("MONGO_URI", "mongodb://mongodb:27017")).fraud_db

# --- SIDEBAR FILTERS ---
st.sidebar.title("🛠️ Analytics Controls")
min_amt = st.sidebar.slider("Minimum Amount Filter", 0, 12000, 0)
show_only_fraud = st.sidebar.toggle("Show High Risk Only", False)

placeholder = st.empty()

while True:
    with placeholder.container():
        # DATA FETCHING
        query = {"amount": {"$gte": min_amt}}
        if show_only_fraud: query["is_fraud"] = True
        
        raw_data = list(db.transactions.find(query).sort("_id", -1).limit(100))
        
        if raw_data:
            df = pd.DataFrame(raw_data)
            
            # --- KPI ROW ---
            st.subheader("🚀 Global Performance Indicators")
            k1, k2, k3, k4 = st.columns(4)
            total = db.transactions.count_documents({})
            frauds = db.transactions.count_documents({"is_fraud": True})
            
            k1.metric("Total Streamed", total)
            k2.metric("Fraud Rate", f"{(frauds/total*100 if total > 0 else 0):.1f}%")
            k3.metric("Avg Risk Score", f"{df['risk_score'].mean():.1f}")
            k4.metric("Active Regions", df['city'].nunique())

            st.markdown("---")

            # --- CHARTS ROW 1: SPATIAL & TRENDS ---
            c1, c2 = st.columns([2, 1])
            
            with c1:
                st.write("🌍 **Live Transaction Map**")
                fig_map = px.scatter_mapbox(df, lat="lat", lon="lon", color="is_fraud", 
                                          size="amount", hover_name="city", zoom=1,
                                          color_discrete_map={True: "#ff4b4b", False: "#00cc96"},
                                          mapbox_style="carto-darkmatter")
                fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, height=400)
                st.plotly_chart(fig_map, use_container_width=True)

            with c2:
                st.write("📱 **Device Vulnerability**")
                fig_device = px.sunburst(df, path=['device', 'is_fraud'], values='amount',
                                       color='is_fraud', color_discrete_map={True: '#ff4b4b', False: '#1f77b4'})
                st.plotly_chart(fig_device, use_container_width=True)

            # --- CHARTS ROW 2: ANALYSIS ---
            c3, c4 = st.columns(2)
            
            with c3:
                st.write("💸 **Risk vs Amount Distribution**")
                fig_scatter = px.scatter(df, x="amount", y="risk_score", color="is_fraud",
                                       trendline="ols", color_discrete_sequence=["#00cc96", "#ff4b4b"])
                st.plotly_chart(fig_scatter, use_container_width=True)

            with c4:
                st.write("📊 **Transaction Type Breakdown**")
                fig_bar = px.bar(df, x="type", y="amount", color="is_fraud", barmode="group")
                st.plotly_chart(fig_bar, use_container_width=True)

            # --- LOGS ---
            st.write("📜 **Real-Time Audit Log**")
            st.dataframe(df[['id', 'amount', 'type', 'city', 'device', 'risk_score', 'is_fraud']].style.background_gradient(cmap='Reds', subset=['risk_score']), use_container_width=True)

        else:
            st.info("📡 Analyzing incoming stream... Please wait.")

    time.sleep(2)