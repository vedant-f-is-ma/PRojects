import streamlit as st
import time
import numpy as np
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Vibe Dashboard", layout="wide", page_icon="🎧")

# --- Custom CSS for Cool Style ---
st.markdown("""
    <style>
    .big-font {
        font-size:60px !important;
        font-weight: bold;
        text-align: center;
        color: #FFFFFF;
        background: linear-gradient(90deg, #e66465, #9198e5);
        padding: 0.5em;
        border-radius: 12px;
    }
    .subtle {
        color: #888888;
        text-align: center;
        font-size: 18px;
    }
    .stButton>button {
        color: white;
        background-color: #6C63FF;
        border-radius: 10px;
        height: 3em;
        width: 100%;
        font-size: 1.2em;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

# --- Title Section ---
st.markdown('<div class="big-font">🎶 Welcome to VibeSpace 🎶</div>', unsafe_allow_html=True)
st.markdown('<div class="subtle">Curated for those who code, create, and chill ✨</div>', unsafe_allow_html=True)

st.markdown("## 🔮 Choose Your Vibe")

# --- Sidebar Inputs ---
vibe = st.sidebar.selectbox("🎧 Pick your vibe:", ["Chill", "Productive", "Party", "Zen"])
theme_color = st.sidebar.color_picker("🎨 Pick your theme color", "#6C63FF")

st.sidebar.markdown("## 📊 Data Explorer")
show_chart = st.sidebar.checkbox("Show some cool data 📈", value=True)

# --- Main Section ---
if vibe == "Chill":
    st.success("🌙 You're in Chill Mode. Lo-fi beats incoming...")
elif vibe == "Productive":
    st.info("🧠 Focus Mode: Get ready to grind.")
elif vibe == "Party":
    st.warning("🎉 Let’s pump up the volume!")
elif vibe == "Zen":
    st.balloons()
    st.write("🧘 You’ve reached inner peace.")

# --- Cool Chart ---
if show_chart:
    st.markdown("## 🎯 Your Random Vibe Chart")
    df = pd.DataFrame({
        "Vibe Score": np.random.randn(100),
        "Time": pd.date_range("2025-01-01", periods=100)
    })
    fig = px.line(df, x="Time", y="Vibe Score", title="Your Live Vibe Signal")
    st.plotly_chart(fig, use_container_width=True)

# --- Interactive Widgets ---
st.markdown("## 🌈 Customize Your Mood")
name = st.text_input("What's your name?")
if name:
    st.write(f"Hey, **{name}**! Stay awesome 💫")

mood = st.radio("How are you feeling today?", ["😄 Happy", "😐 Meh", "😢 Sad", "🔥 Inspired"])
if st.button("Send Vibe"):
    st.success(f"Vibe sent: {mood}")

# --- Footer ---
st.markdown("---")
st.markdown("Made with ❤️ in Streamlit")

