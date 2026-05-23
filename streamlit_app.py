import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import time

st.set_page_config(page_title="🕸️ STEEL NET SENTINEL", layout="wide")
st.title("🕸️ STEEL NET SENTINEL")
st.subheader("Dynamiczna siatka przeciwlotnicza Stalowej Woli • Live C-UAS Symulacja")

# Sidebar
st.sidebar.title("🎮 Kontrola misji")
attack_btn = st.sidebar.button("🚀 URUCHOM ATAK DRONA", type="primary", use_container_width=True)
jamming = st.sidebar.checkbox("📡 WŁĄCZ JAMMING (symulacja zakłóceń)", value=False)

center_lat, center_lon = 50.582, 22.053

# Radary
radars = pd.DataFrame({
    'lat': [50.620, 50.545, 50.605, 50.565],
    'lon': [21.985, 22.125, 22.005, 22.105],
    'name': ['Radar NORTH', 'Radar SOUTH', 'Radar WEST', 'Radar EAST']
})

# Punkty startu swarmu (straż, policja, wojsko)
launch_points = pd.DataFrame({
    'lat': [50.575, 50.590, 50.565],
    'lon': [22.040, 22.065, 22.020],
    'name': ['Straż Pożarna', 'Komisariat', 'Jednostka Kryzysowa']
})

if 'frame' not in st.session_state:
    st.session_state.frame = 0
if 'running' not in st.session_state:
    st.session_state.running = False
if 'attacker_path_lat' not in st.session_state:
    st.session_state.attacker_path_lat = []
if 'attacker_path_lon' not in st.session_state:
    st.session_state.attacker_path_lon = []

fig = go.Figure()

if attack_btn or st.session_state.running:
    st.session_state.running = True
    frame = st.session_state.frame

    # === TRAJEKTORIA ATAKUJĄCEGO DRONA ===
    attacker_lat = 50.620 - (50.620 - 50.582) * (frame / 35)
    attacker_lon = 21.985 + (22.053 - 21.985) * (frame / 35)
    
    st.session_state.attacker_path_lat.append(attacker_lat)
    st.session_state.attacker_path_lon.append(attacker_lon)

    # Przewidywana trajektoria (dashed line)
    pred_lats = [attacker_lat, 50.582]
    pred_lons = [attacker_lon, 22.053]

    # Swarm startuje od frame 12
    swarm_active = frame >= 12

    # === GŁÓWNA FIGURA ===
    # 1. Ścieżka drona (historia)
    fig.add_trace(go.Scattermapbox(
        lat=st.session_state.attacker_path_lat,
        lon=st.session_state.attacker_path_lon,
        mode='lines',
        line=dict(width=5, color='red'),
        name='Dron atakujący (ścieżka)'
    ))

    # 2. Aktualna pozycja drona (marker)
    fig.add_trace(go.Scattermapbox(
        lat=[attacker_lat], lon=[attacker_lon],
        mode='markers',
        marker=dict(size=18, color='red', symbol='circle'),
        name='Dron atakujący'
    ))

    # 3. Przewidywana trajektoria
    fig.add_trace(go.Scattermapbox(
        lat=pred_lats, lon=pred_lons,
        mode='lines',
        line=dict(width=3, color='orange', dash='dash'),
        name='Przewidywana trajektoria'
    ))

    # 4. Radary (podświetlamy wykryty)
    detected_idx = 0 if frame > 5 else -1
    radar_colors = ['lime' if i == detected_idx else 'darkred' for i in range(len(radars))]
    fig.add_trace(go.Scattermapbox(
        lat=radars['lat'], lon=radars['lon'],
        mode='markers+text',
        marker=dict(size=22, color=radar_colors, symbol='square'),
        text=radars['name'], textposition='top center',
        name='Radary'
    ))

    # 5. Punkty startu swarmu
    fig.add_trace(go.Scattermapbox(
        lat=launch_points['lat'], lon=launch_points['lon'],
        mode='markers+text',
        marker=dict(size=16, color='blue', symbol='star'),
        text=launch_points['name'], textposition='bottom center',
        name='Punkty startu swarmu'
    ))

    # 6. Swarm + siatka (jeśli aktywny)
    if swarm_active:
        for i in range(6):
            t = min(1.0, (frame - 12) / 20)
            inter_lat = launch_points.iloc[i % 3]['lat'] + (attacker_lat - launch_points.iloc[i % 3]['lat']) * t
            inter_lon = launch_points.iloc[i % 3]['lon'] + (attacker_lon - launch_points.iloc[i % 3]['lon']) * t
            
            fig.add_trace(go.Scattermapbox(
                lat=[inter_lat], lon=[inter_lon],
                mode='markers',
                marker=dict(size=14, color='lime', symbol='triangle-up'),
                name=f'Interceptor {i+1}'
            ))
            
            # Linie siatki
            if i > 0:
                prev_lat = launch_points.iloc[(i-1) % 3]['lat'] + (attacker_lat - launch_points.iloc[(i-1) % 3]['lat']) * t
                prev_lon = launch_points.iloc[(i-1) % 3]['lon'] + (attacker_lon - launch_points.iloc[(i-1) % 3]['lon']) * t
                fig.add_trace(go.Scattermapbox(
                    lat=[inter_lat, prev_lat], lon=[inter_lon, prev_lon],
                    mode='lines',
                    line=dict(width=3.5, color='cyan'),
                    name='Siatka'
                ))

    fig.update_layout(
        mapbox=dict(style="open-street-map", center=dict(lat=center_lat, lon=center_lon), zoom=12.5),
        margin=dict(l=0, r=0, t=0, b=0),
        height=650,
        showlegend=True,
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
    )

    st.plotly_chart(fig, use_container_width=True, key=f"sim_{frame}")

    # Statusy
    col1, col2, col3 = st.columns(3)
    with col1: st.metric("Radar wykrył", "RADAR NORTH" if frame > 5 else "—", "w 3.2s")
    with col2: st.metric("Swarm aktywny", "TAK" if swarm_active else "NIE", f"frame {frame}")
    with col3: st.metric("Czas do interceptu", f"{max(0, 35-frame)}s")

    if jamming:
        st.warning("📡 JAMMING AKTYWNY – system przełączył się na on-board AI prediction")

    st.session_state.frame += 1
    if st.session_state.frame < 40:
        time.sleep(0.22)
        st.rerun()
    else:
        st.success("✅ SIATKA ZAMKNIĘTA! Cel przechwycony 800 m przed infrastrukturą krytyczną.")
        st.balloons()
        st.session_state.running = False
        st.session_state.frame = 0
        st.session_state.attacker_path_lat = []
        st.session_state.attacker_path_lon = []

else:
    # Startowa mapa
    empty_fig = go.Figure()
    empty_fig.update_layout(
        mapbox=dict(style="open-street-map", center=dict(lat=center_lat, lon=center_lon), zoom=12.5),
        margin=dict(l=0, r=0, t=30, b=0),
        height=650
    )
    st.plotly_chart(empty_fig, use_container_width=True)

st.caption("Steel Net Sentinel • SpaceShield Hack 2026 • DEFENCE • Real-time symulacja przechwycenia drona")