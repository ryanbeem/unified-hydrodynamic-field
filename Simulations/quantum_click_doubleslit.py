import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ---------------------------------------------------------
# Simulation Setup & Parameters
# ---------------------------------------------------------
fps = 30
duration_sec = 12
total_frames = fps * duration_sec

num_detectors = 400
x_screen = np.linspace(-10, 10, num_detectors)

# Double-slit interference pressure profile (Continuous Wavefront)
d_slit = 1.6  # Slit separation
w_slit = 0.5  # Slit width
k_wave = 2.0  # Wavenumber

# Classical double-slit intensity profile across detector face
double_slit_envelope = (np.sinc(w_slit * x_screen / np.pi)**2) * (np.cos(d_slit * x_screen)**2)
P_wave_peak = 1.2
P_wave = P_wave_peak * double_slit_envelope

# Hydrostatic Threshold & Noise Parameters
Phi_threshold = 1.55       # Rigid atomic compliance threshold
noise_std = 0.38          # Zero-point pressure fluctuation amplitude (delta P_bg)

# Hit accumulator
click_history = []

# ---------------------------------------------------------
# Matplotlib Figure & Layout Setup
# ---------------------------------------------------------
plt.style.use('dark_background')
fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(13, 8), gridspec_kw={'height_ratios': [1, 1.1]})
fig.suptitle(r"Deterministic 'Quantum Click' Assembly: Continuous Wave + Hydrostatic Tipping Point",
             fontsize=13, fontweight='bold', y=0.98)

# Top Panel: Real-Time Pressure Field at Detector Array
ax_top.set_xlim(-10, 10)
ax_top.set_ylim(-0.2, 2.3)
ax_top.set_title(r"Real-Time Detector Surface Pressure: $P_{\mathrm{wave}}(x) + \delta P_{\mathrm{bg}}(x, t)$", 
                 fontsize=11, color='#00d2ff', pad=8)
ax_top.set_ylabel("Hydrostatic Pressure", fontsize=10)

# Static Curves in Top Panel
ax_top.plot(x_screen, P_wave, color='#00d2ff', linestyle='--', alpha=0.6, label=r"Continuous Wave $P_{\mathrm{wave}}(x)$")
ax_top.axhline(Phi_threshold, color='#ff3366', linewidth=1.8, linestyle='-', label=r"Compliance Threshold $\Phi_{\mathrm{threshold}}$")

# Dynamic Objects in Top Panel
line_total_pressure, = ax_top.plot([], [], color='#ffffff', lw=1.0, alpha=0.85, label=r"Total Surface Pressure")
scatter_breaches, = ax_top.plot([], [], 'o', color='#ff3366', markersize=7, label="Threshold Breaches ('Clicks')")

ax_top.legend(loc='upper right', framealpha=0.6, fontsize=9)

# Bottom Panel: Accumulated Hits (The "Interference Pattern" Building Up)
ax_bottom.set_xlim(-10, 10)
ax_bottom.set_ylim(0, 1)
ax_bottom.set_title("Accumulated Discrete Detections Over Time (No Wavefunction Collapse)", 
                    fontsize=11, color='#00ff99', pad=8)
ax_bottom.set_xlabel("Detector Screen Coordinate $x$", fontsize=10)
ax_bottom.set_ylabel("Normalized Hit Density", fontsize=10)

# Histogram & Density Objects
bins = np.linspace(-10, 10, 80)
n_counts, _, patches = ax_bottom.hist([], bins=bins, color='#00ff99', alpha=0.65, edgecolor='#004d26', density=True)
line_expected, = ax_bottom.plot(x_screen, P_wave / np.trapz(P_wave, x_screen), color='#00d2ff', lw=1.5, ls='--', label="Expected Wave Intensity")

ax_bottom.legend(loc='upper right', framealpha=0.6, fontsize=9)

# ---------------------------------------------------------
# Animation Update Loop
# ---------------------------------------------------------
def animate(frame):
    global click_history
    
    # 1. Generate stochastic zero-point pressure noise delta P_bg(x, t)
    delta_P_bg = np.random.normal(0, noise_std, size=num_detectors)
    
    # 2. Total pressure striking the detector array
    P_total = P_wave + delta_P_bg
    
    # 3. Deterministic Tipping Point Condition
    breaches_mask = P_total >= Phi_threshold
    breach_x = x_screen[breaches_mask]
    breach_P = P_total[breaches_mask]
    
    # Append detected click positions to global history
    if len(breach_x) > 0:
        click_history.extend(breach_x)
    
    # Update Top Panel Lines
    line_total_pressure.set_data(x_screen, P_total)
    scatter_breaches.set_data(breach_x, breach_P)
    
    # Update Bottom Panel Histogram
    ax_bottom.cla()
    ax_bottom.set_xlim(-10, 10)
    ax_bottom.set_title("Accumulated Discrete Detections Over Time (No Wavefunction Collapse)", 
                        fontsize=11, color='#00ff99', pad=8)
    ax_bottom.set_xlabel("Detector Screen Coordinate $x$", fontsize=10)
    ax_bottom.set_ylabel("Normalized Hit Density", fontsize=10)
    
    if len(click_history) > 5:
        ax_bottom.hist(click_history, bins=bins, color='#00ff99', alpha=0.65, edgecolor='#004d26', density=True)
    
    ax_bottom.plot(x_screen, P_wave / np.trapz(P_wave, x_screen), color='#00d2ff', lw=1.5, ls='--', label="Expected Wave Intensity")
    
    # Update Status Box
    total_clicks = len(click_history)
    text_stats_str = (
        f"Frame: {frame}/{total_frames}\n" +
        f"Clicks Recorded: {total_clicks}\n" +
        r"Mechanism: $P_{\mathrm{wave}} + \delta P_{\mathrm{bg}} \geq \Phi_{\mathrm{threshold}}$" + "\n" +
        "Determinism: 100% (Zero Probabilistic Collapse)"
    )
    ax_bottom.text(0.02, 0.72, text_stats_str, transform=ax_bottom.transAxes, fontsize=9,
                   bbox=dict(boxstyle='round', facecolor='#1e1e1e', alpha=0.85, edgecolor='#00ff99'))
    
    ax_bottom.legend(loc='upper right', framealpha=0.6, fontsize=9)
    
    return [line_total_pressure, scatter_breaches]

# ---------------------------------------------------------
# Render Window
# ---------------------------------------------------------
plt.tight_layout()
fig.subplots_adjust(top=0.91, hspace=0.35)

anim = FuncAnimation(fig, animate, frames=total_frames, interval=1000/fps, blit=False)

plt.show()