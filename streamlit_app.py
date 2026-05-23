import streamlit as st
from streamlit_folium import st_folium
import folium
import time

st.set_page_config(page_title="🕸️ STEEL NET SENTINEL", layout="wide")
st.title("🕸️ STEEL NET SENTINEL")
st.subheader("Dynamiczna siatka przeciwlotnicza Stalowej Woli • Live C-UAS Symulacja")

# Sidebar
st.sidebar.title("🎮 Kontrola misji")
attack_btn = st.sidebar.button("🚀 URUCHOM ATAK DRONA", type="primary", use_container_width=True)
jamming = st.sidebar.checkbox("📡 WŁĄCZ JAMMING (symulacja zakłóceń)", value=False)

# Centrum Stalowej Woli
center_lat, center_lon = 50.582, 22.053

# Radary na obrzeżach
radars = [
    {"name": "Radar NORTH", "lat": 50.620, "lon": 21.985},
    {"name": "Radar SOUTH", "lat": 50.545, "lon": 22.125},
    {"name": "Radar WEST",  "lat": 50.605, "lon": 22.005},
    {"name": "Radar EAST",  "lat": 50.565, "lon": 22.105}
]

# Punkty startu swarmu (jednostki kryzysowe)
launch_points = [
    {"name": "Straż Pożarna", "lat": 50.575, "lon": 22.040},
    {"name": "Komisariat",     "lat": 50.590, "lon": 22.065},
    {"name": "Jednostka Kryzysowa", "lat": 50.565, "lon": 22.020}
]

# Sesja stanu
if 'frame' not in st.session_state:
    st.session_state.frame = 0
if 'running' not in st.session_state:
    st.session_state.running = False

# === TWORZENIE MAPY ===
m = folium.Map(location=[center_lat, center_lon], zoom_start=13, tiles="OpenStreetMap")

# Radary (statyczne + podświetlenie)
for i, r in enumerate(radars):
    color = "lime" if (st.session_state.running and st.session_state.frame > 5 and i == 0) else "red"
    folium.CircleMarker(
        location=[r["lat"], r["lon"]],
        radius=15,
        color=color,
        fill=True,
        popup=r["name"]
    ).add_to(m)

# Punkty startu swarmu
for p in launch_points:
    folium.Marker(
        location=[p["lat"], p["lon"]],
        popup=p["name"],
        icon=folium.Icon(color="blue", icon="star")
    ).add_to(m)

# === JEŚLI SYMULACJA DZIAŁA ===
if attack_btn or st.session_state.running:
    st.session_state.running = True
    frame = st.session_state.frame

    # Dron atakujący (ruch po linii)
    attacker_lat = 50.620 - (50.620 - 50.582) * (frame / 35)
    attacker_lon = 21.985 + (22.053 - 21.985) * (frame / 35)

    # Marker drona
    folium.Marker(
        location=[attacker_lat, attacker_lon],
        popup="Dron atakujący",
        icon=folium.Icon(color="red", icon="plane")
    ).add_to(m)

    # Przewidywana trajektoria (linia)
    folium.PolyLine(
        locations=[[attacker_lat, attacker_lon], [50.582, 22.053]],
        color="orange",
        weight=4,
        dash_array="10, 10",
        popup="Przewidywana trajektoria"
    ).add_to(m)

    # Swarm + siatka (od frame 12)
    if frame >= 12:
        for i in range(6):
            t = min(1.0, (frame - 12) / 20)
            inter_lat = launch_points[i % 3]["lat"] + (attacker_lat - launch_points[i % 3]["lat"]) * t
            inter_lon = launch_points[i % 3]["lon"] + (attacker_lon - launch_points[i % 3]["lon"]) * t

            folium.Marker(
                location=[inter_lat, inter_lon],
                icon=folium.Icon(color="green", icon="arrow-up")
            ).add_to(m)

            # Linie siatki
            if i > 0:
                prev_lat = launch_points[(i-1) % 3]["lat"] + (attacker_lat - launch_points[(i-1) % 3]["lat"]) * t
                prev_lon = launch_points[(i-1) % 3]["lon"] + (attacker_lon - launch_points[(i-1) % 3]["lon"]) * t
                folium.PolyLine(
                    locations=[[inter_lat, inter_lon], [prev_lat, prev_lon]],
                    color="cyan",
                    weight=5
                ).add_to(m)

    # Statusy
    st.info(f"🔴 Symulacja w toku – frame {frame}/40 | Dron w drodze...")
    if jamming:
        st.warning("📡 JAMMING AKTYWNY – system na on-board AI prediction!")

    # Render mapy
    st_folium(m, width=900, height=650, returned_objects=[])

    st.session_state.frame += 1
    if st.session_state.frame < 40:
        time.sleep(0.25)
        st.rerun()
    else:
        st.success("✅ SIATKA ZAMKNIĘTA! Cel przechwycony 800 m przed infrastrukturą krytyczną.")
        st.balloons()
        st.session_state.running = False
        st.session_state.frame = 0

else:
    # Startowa mapa (zawsze pokazuje mapę Stalowej Woli)
    st_folium(m, width=900, height=650, returned_objects=[])

st.caption("Steel Net Sentinel • SpaceShield Hack 2026 • DEFENCE track • Real-time symulacja")