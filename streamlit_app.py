import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import time

st.set_page_config(page_title="Steel Net Sentinel", layout="wide")
st.title("🕸️ STEEL NET SENTINEL")
st.subheader("Dynamiczna siatka przeciwlotnicza Stalowej Woli")

# Sidebar controls
st.sidebar.title("Kontrola misji")
attack_btn = st.sidebar.button("🚀 Uruchom atak drona", type="primary")
jamming = st.sidebar.checkbox("📡 Włącz jamming (symulacja zakłóceń)")

# Mapa Stalowej Woli
center_lat, center_lon = 50.582, 22.053
m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="OpenStreetMap")

# Radary na obrzeżach (czerwone)
radars = [
    [50.62, 21.98], [50.55, 22.13], [50.60, 22.00], [50.57, 22.10]
]
for r in radars:
    folium.CircleMarker(r, radius=12, color="red", fill=True, popup="Radar").add_to(m)

# Obiekty krytyczne (niebieskie)
critical = [
    {"loc": [50.58, 22.05], "name": "Huta Stalowa Wola"},
    {"loc": [50.59, 22.06], "name": "Elektrownia"},
    {"loc": [50.57, 22.04], "name": "Wodociągi"},
]
for c in critical:
    folium.Marker(c["loc"], popup=c["name"], icon=folium.Icon(color="blue")).add_to(m)

# Sesja stanu do symulacji
if "simulation_running" not in st.session_state:
    st.session_state.simulation_running = False
if "frame" not in st.session_state:
    st.session_state.frame = 0

col1, col2 = st.columns([3, 1])

with col1:
    map_data = st_folium(m, width=800, height=600, returned_objects=["last_object_clicked"])

    if attack_btn and not st.session_state.simulation_running:
        st.session_state.simulation_running = True
        st.session_state.frame = 0
        st.rerun()

    if st.session_state.simulation_running:
        st.info("🔴 SYMULACJA W TOKU – dron w drodze...")
        
        # Prosta animacja tekstowa + rerun
        progress = st.progress(st.session_state.frame / 30)
        st.write(f"Klatka: {st.session_state.frame}/30 | Trajektoria obliczana...")

        if jamming:
            st.warning("📡 JAMMING AKTYWNY – system przełącza się na on-board AI prediction!")

        # Symulacja siatki (po 15 klatkach)
        if st.session_state.frame >= 15:
            st.success("🕸️ SWARM INTERCEPTORÓW WYSTRZELONY – SIATKA SIĘ ZAMYKA!")
            st.balloons()

        st.session_state.frame += 1
        if st.session_state.frame < 30:
            time.sleep(0.3)
            st.rerun()
        else:
            st.session_state.simulation_running = False
            st.success("✅ PRZECHWYCONO! Cel zneutralizowany przed infrastrukturą krytyczną.")

with col2:
    st.subheader("Status systemu")
    st.metric("Radary aktywne", "4/4", "100%")
    st.metric("Gotowość swarmu", "6 dronów", "ONLINE")
    st.metric("Czas reakcji", "4.2 s", "-0.8 s")

st.caption("Steel Net Sentinel © SpaceShield Hack 2026 | DEFENCE track")
