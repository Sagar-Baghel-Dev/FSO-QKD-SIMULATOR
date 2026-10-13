import streamlit as st
import plotly.graph_objects as go
import numpy as np

# Page Setup
st.set_page_config(page_title="FSO-QKD Visual Demo", layout="wide")
st.title("🛰️ FSO-QKD Atmospheric Simulation Platform (Visual Layout Demo)")
st.markdown("Yeh final project ka visual structure hai (Without heavy backend physics)")

# Sidebar Layout (Strict Inputs as per PRD)
st.sidebar.header("1. Link Geometry")
st.sidebar.text_input("Propagation Distance (km)", "300")
st.sidebar.text_input("TX Altitude (m)", "15")

st.sidebar.header("2. Atmosphere & Turbulence")
st.sidebar.text_input("Base Cn2 (m^-2/3)", "1e-14")
st.sidebar.text_input("Outer Scale L0 (m)", "5.0")

st.sidebar.header("3. QKD Settings")
st.sidebar.selectbox("Protocol", ["Decoy-state BB84", "E91"])

# Main 3D Earth Curvature Visualization
st.subheader("🌍 1. Main View: Earth Curvature & Curved Beam Trajectory")
st.markdown("Laser flat nahi jayega, balki zameen ki golai (Earth Curvature) ke upar se arc banate hue jayega.")

fig = go.Figure()

# Create a simple 3D Globe surface
u = np.linspace(0, 2 * np.pi, 60)
v = np.linspace(0, np.pi/4, 30) # Showing only top hemisphere
R_earth = 6371
x = R_earth * np.outer(np.cos(u), np.sin(v))
y = R_earth * np.outer(np.sin(u), np.sin(v))
z = R_earth * np.outer(np.ones(np.size(u)), np.cos(v))
fig.add_surface(x=x, y=y, z=z, opacity=0.4, colorscale="Blues", showscale=False, name="Earth Surface")

# Create a curved laser beam arc
t = np.linspace(0, 1, 100)
arc_angle = t * 0.05 # Simulate distance travel angle
arc_x = R_earth * np.cos(arc_angle)
arc_y = R_earth * np.sin(arc_angle)
# Beam height increases in the middle due to curvature
arc_z = R_earth + (50 * np.sin(t * np.pi)) 
fig.add_scatter3d(x=arc_x, y=arc_y, z=arc_z, mode='lines+markers', 
                  marker=dict(size=2, color='red'), 
                  line=dict(color='red', width=5), name="FSO Laser Path")

fig.update_layout(scene=dict(xaxis_title='X (km)', yaxis_title='Y (km)', zaxis_title='Altitude (km)',
                             aspectmode='data'), height=600, margin=dict(l=0, r=0, b=0, t=0))
st.plotly_chart(fig, use_container_width=True)

# Secondary Section: Phase Screens & Physics
st.markdown("---")
st.subheader("📊 2. Detailed Physics Inspection")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Phase Screen (Atmospheric Turbulence)**")
    st.info("Yahan random turbulence ki 2D colored image aayegi.")
    st.image("https://via.placeholder.com/300x200.png?text=Turbulence+Phase+Screen", use_column_width=True)

with col2:
    st.markdown("**Intensity & Scintillation**")
    st.info("Yahan laser ka toota hua (speckled) roop dikhega.")
    st.image("https://via.placeholder.com/300x200.png?text=Beam+Intensity+Profile", use_column_width=True)

with col3:
    st.markdown("**QKD Performance**")
    st.metric("Estimated Channel Transmittance", "45.2 %", "-2.1 % loss due to scatter")
    st.metric("Quantum Bit Error Rate (QBER)", "3.1 %", "Secure")
    st.metric("Secret Key Rate", "1.2 kbps")