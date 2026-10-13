import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Advanced Long-Range FSO-QKD Simulator",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS styling for a research-grade look
st.markdown("""
    <style>
    .main-title { font-size: 28px; font-weight: 700; color: #1E3A8A; }
    .sub-text { font-size: 15px; color: #4B5563; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">🛰️ Advanced Long-Range FSO-QKD Atmospheric Simulator</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-text">Upgraded for Inter-Satellite / Deep Ground Links (100 - 500 km) with Earth Curvature & Live Animation</p>', unsafe_allow_html=True)
st.markdown("---")

# --- SIDEBAR: PRECISION TEXT & NUMBER INPUTS ---
st.sidebar.header("⚙️ Simulation Configuration")

st.sidebar.subheader("1. Propagation Geometry")
dist_str = st.sidebar.text_input("Propagation Distance (km)", value="300.0")
wavelength_str = st.sidebar.text_input("Laser Wavelength (nm)", value="1550.0")  # Telecom IR band for long range
w0_str = st.sidebar.text_input("Initial Beam Waist w0 (mm)", value="150.0")

st.sidebar.subheader("2. Atmospheric & Meteorological Factors")
temp_str = st.sidebar.text_input("Surface Temperature (°C)", value="22.5")
press_str = st.sidebar.text_input("Atmospheric Pressure (hPa)", value="1013.25")
humidity_str = st.sidebar.text_input("Relative Humidity (%)", value="45.0")
base_cn2_str = st.sidebar.text_input("Base Turbulence Cn2 (m^-2/3)", value="1e-14")

st.sidebar.subheader("3. Animation & Segmentation Settings")
num_screens = st.sidebar.slider("Phase Screen Segments (Steps)", min_value=10, max_value=100, value=30, step=5)
animation_speed = st.sidebar.slider("Animation Delay (sec)", min_value=0.01, max_value=0.2, value=0.05, step=0.01)

# Safe Parsing of Inputs
try:
    Z_km = float(dist_str)
    wavelength_nm = float(wavelength_str)
    w0_mm = float(w0_str)
    temperature = float(temp_str) + 273.15  # Kelvin
    pressure = float(press_str)
    humidity = float(humidity_str)
    base_cn2 = float(base_cn2_str)
except ValueError:
    st.sidebar.error("⚠️ Invalid text input detected. Please enter valid numeric values.")
    Z_km, wavelength_nm, w0_mm, temperature, pressure, humidity, base_cn2 = 300.0, 1550.0, 150.0, 295.15, 1013.25, 45.0, 1e-14

Z_total = Z_km * 1000.0  # Meters
wavelength = wavelength_nm * 1e-9
W0 = w0_mm * 1e-3

# --- CORE PHYSICS & GRID SETUP ---
N = 256
L = 3.0  # Physical grid size in meters
dx = L / N
k = 2 * np.pi / wavelength

x = np.linspace(-L/2, L/2, N)
X, Y = np.meshgrid(x, x)
fx = np.fft.fftfreq(N, dx)
FX, FY = np.meshgrid(fx, fx)
K_transverse_sq = (2 * np.pi * FX)**2 + (2 * np.pi * FY)**2

# Earth Curvature & Altitude-dependent Turbulence (Hufnagel-Valley style adjustment)
def get_atmospheric_profile(z_current, total_z):
    R_earth = 6371e3  # Radius of Earth in meters
    # Geometric height due to Earth's curvature in a curved link
    h_curvature = (z_current * (total_z - z_current)) / (2 * R_earth)
    
    # Humidity and pressure attenuation factor mockup
    humidity_factor = 1.0 + (humidity / 100.0) * 0.1
    
    # Cn2 drops exponentially with altitude above Earth surface
    cn2_altitude = base_cn2 * np.exp(-h_curvature / 1500.0) * humidity_factor
    return h_curvature, cn2_altitude

def generate_phase_screen(cn2_val, dz):
    f_spatial = np.sqrt(FX**2 + FY**2)
    f_spatial[0, 0] = 1.0  
    r0 = max(0.01, (0.423 * k**2 * cn2_val * dz)**(-3/5))
    PSD_phi = 0.023 * (r0**(-5/3)) * (f_spatial**(-11/3))
    PSD_phi[0, 0] = 0.0  
    noise = np.random.randn(N, N) + 1j * np.random.randn(N, N)
    cn = noise * np.sqrt(PSD_phi) * (1.0 / (N * dx))
    return np.real(np.fft.ifft2(cn)) * (N**2)

# --- MAIN INTERFACE & ANIMATION CONTROL ---
col_run, col_info = st.columns([1, 3])
with col_run:
    run_animation = st.button("🚀 Run Live Beam Animation", type="primary", use_container_width=True)

with col_info:
    st.info(f"**Target Specs:** Link Range: **{Z_km} km** | Wavelength: **{wavelength_nm} nm** | Grid Resolution: **{N}x{N}**")

st.markdown("---")

# Layout for Live Simulation
if run_animation:
    st.subheader("🎥 Live Phase-Screen Segmented Propagation & Animation")
    
    # Create placeholders for dynamic updates
    anim_placeholder = st.empty()
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    progress_bar = st.progress(0)
    
    dz = Z_total / num_screens
    H_step = np.exp(-1j * (K_transverse_sq / (2 * k)) * dz)
    E_curr = np.exp(-(X**2 + Y**2) / W0**2).astype(complex)
    
    extent_cm = [-L/2 * 100, L/2 * 100, -L/2 * 100, L/2 * 100]
    
    # Step-by-step simulation loop
    for step in range(num_screens):
        current_z = (step + 1) * dz
        h_curv, cn2_local = get_atmospheric_profile(current_z, Z_total)
        
        # Apply turbulence phase screen and diffraction step
        phase_screen = generate_phase_screen(cn2_local, dz)
        E_curr = E_curr * np.exp(1j * phase_screen)
        E_curr = np.fft.ifft2(np.fft.fft2(E_curr) * H_step)
        
        intensity = np.abs(E_curr)**2
        peak_intensity = np.max(intensity)
        beam_width_current = np.sqrt(np.sum(X**2 * intensity) / np.sum(intensity)) * 100  # cm
        
        # Live Metrics Update
        with metric_col1:
            st.metric("Propagation Distance", f"{current_z/1000:.1f} km")
        with metric_col2:
            st.metric("Local Turbulence ($C_n^2$)", f"{cn2_local:.2e}")
        with metric_col3:
            st.metric("Earth Curvature Height", f"{h_curv:.1f} m")
        with metric_col4:
            st.metric("Peak Intensity", f"{peak_intensity:.2f}")
            
        # Render Live Plot
        fig, ax = plt.subplots(figsize=(7, 4.5))
        im = ax.imshow(intensity, cmap='jet', extent=extent_cm)
        ax.set_title(f"Segment {step+1}/{num_screens} | Distance: {current_z/1000:.1f} km")
        ax.set_xlabel("X Transverse (cm)")
        ax.set_ylabel("Y Transverse (cm)")
        plt.colorbar(im, ax=ax, label="Intensity")
        
        anim_placeholder.pyplot(fig)
        plt.close(fig)
        
        progress_bar.progress((step + 1) / num_screens)
        time.sleep(animation_speed)
        
    st.success("✨ Long-range animated propagation completed successfully across all atmospheric segments!")
else:
    st.markdown("""
        ### 📌 How to use this Upgraded Simulator:
        1. **Configure Parameters:** Modify the distance (up to 500 km), wavelength, and surface weather factors (Temperature, Pressure, Humidity) in the sidebar.
        2. **Adjust Segments:** Choose how many phase-screen segmentation steps you want for smooth animation.
        3. **Run Animation:** Click the **'Run Live Beam Animation'** button above to visualize the laser beam breaking down, shifting, and propagating through curved atmospheric layers step-by-step.
    """)