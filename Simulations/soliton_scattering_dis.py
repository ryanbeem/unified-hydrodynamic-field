import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ---------------------------------------------------------
# Simulation Setup & Parameters
# ---------------------------------------------------------
fps = 30
duration_sec = 10
total_frames = fps * duration_sec

x_pts = 800
x_grid = np.linspace(-10, 10, x_pts)

# Physics parameters
v_probe = 0.18               # Forward propagation velocity
impact_frame = 50            # Frame at which probe strikes center soliton (x = 0)

# ---------------------------------------------------------
# Matplotlib Figure & Layout Setup
# ---------------------------------------------------------
plt.style.use('dark_background')
fig, (ax_elastic, ax_dis) = plt.subplots(2, 1, figsize=(13, 8.5), gridspec_kw={'height_ratios': [1, 1]})
fig.suptitle(r"Soliton Collision Mechanics: Elastic Surface Bounce vs. DIS Resonant Unzipping", 
             fontsize=13, fontweight='bold', y=0.98)

# Top Panel: Low-Energy Elastic Scattering (Q^2 <= 1.0 GeV^2)
ax_elastic.set_xlim(-10, 10)
ax_elastic.set_ylim(-0.2, 2.2)
ax_elastic.set_title(r"Low-Energy Elastic Regime ($Q^2 \leq 1.0\ \mathrm{GeV}^2$): Poloidal Surface Reflection ($Q_H = 1$ Preserved)", 
                     fontsize=11, color='#00d2ff', pad=8)
ax_elastic.set_ylabel("Field Energy Density", fontsize=10)
ax_elastic.axhline(0, color='gray', lw=0.5, ls='--')

line_elastic_core, = ax_elastic.plot([], [], color='#00d2ff', lw=2.2, label=r"Soliton Core ($Q_H=1$)")
line_elastic_probe, = ax_elastic.plot([], [], color='#ff7f0e', lw=1.8, label=r"Low-$Q^2$ Probe Wave")

text_elastic = ax_elastic.text(0.02, 0.62, '', transform=ax_elastic.transAxes, fontsize=9,
                               bbox=dict(boxstyle='round', facecolor='#1e1e1e', alpha=0.85, edgecolor='#00d2ff'))
ax_elastic.legend(loc='upper right', framealpha=0.6, fontsize=9)

# Bottom Panel: High-Energy DIS Resonant Unzipping (Q^2 >> 1.0 GeV^2)
ax_dis.set_xlim(-10, 10)
ax_dis.set_ylim(-0.2, 2.2)
ax_dis.set_title(r"High-Energy DIS Regime ($Q^2 \gg 1.0\ \mathrm{GeV}^2$): Parametric Resonant Node Unzipping ($Q_H \to 0$)", 
                 fontsize=11, color='#ff3366', pad=8)
ax_dis.set_xlabel("Spatial Axis $x$", fontsize=10)
ax_dis.set_ylabel("Field Energy Density", fontsize=10)
ax_dis.axhline(0, color='gray', lw=0.5, ls='--')

line_dis_core, = ax_dis.plot([], [], color='#00ff99', lw=2.2, label=r"Soliton Core Envelope")
line_dis_probe, = ax_dis.plot([], [], color='#ff3366', lw=1.5, label=r"High-$Q^2$ Resonant Probe / Fragments")

text_dis = ax_dis.text(0.02, 0.62, '', transform=ax_dis.transAxes, fontsize=9,
                        bbox=dict(boxstyle='round', facecolor='#1e1e1e', alpha=0.85, edgecolor='#ff3366'))
ax_dis.legend(loc='upper right', framealpha=0.6, fontsize=9)

# ---------------------------------------------------------
# Animation Update Loop
# ---------------------------------------------------------
def animate(frame):
    t = frame
    
    # =====================================================
    # 1. Low-Energy Elastic Scattering (Top Panel)
    # =====================================================
    if t < impact_frame:
        x_p = -8.0 + v_probe * t
        probe_elastic = 0.6 * np.exp(-((x_grid - x_p)/1.5)**2) * (np.cos(1.2 * (x_grid - x_p))**2)
        core_elastic = 1.2 * np.exp(-(x_grid/1.0)**2)
        q_h_elastic = 1.000
        status_elastic = "Approaching Soliton Boundary"
    else:
        dt = t - impact_frame
        x_refl = -v_probe * dt
        x_trans = v_probe * dt
        
        refl_wave = 0.45 * np.exp(-((x_grid - x_refl)/1.5)**2) * (np.cos(1.2 * (x_grid - x_refl))**2)
        trans_wave = 0.15 * np.exp(-((x_grid - x_trans)/1.5)**2) * (np.cos(1.2 * (x_grid - x_trans))**2)
        probe_elastic = refl_wave + trans_wave
        
        # Core vibrates smoothly without topological destruction
        core_elastic = 1.2 * np.exp(-(x_grid/1.0)**2) * (1.0 + 0.08 * np.sin(0.4 * dt) * np.exp(-dt/20.0))
        q_h_elastic = 1.000
        status_elastic = "Elastic Surface Bounce (Smooth Poloidal Deflection)"
        
    line_elastic_core.set_data(x_grid, core_elastic)
    line_elastic_probe.set_data(x_grid, probe_elastic)
    
    text_elastic.set_text(
        f"Frame: {t}/{total_frames}\n" +
        rf"Topological Charge $Q_H$: {q_h_elastic:.3f} (Conserved)" + "\n" +
        rf"Status: {status_elastic}" + "\n" +
        r"Mechanic: Smooth 2D Poloidal Integration (No Quark Point-Partons)"
    )

    # =====================================================
    # 2. High-Energy DIS Resonant Unzipping (Bottom Panel)
    # =====================================================
    if t < impact_frame:
        x_p = -8.0 + v_probe * t
        probe_dis = 0.8 * np.exp(-((x_grid - x_p)/0.7)**2) * (np.cos(5.0 * (x_grid - x_p))**2)
        core_dis = 1.2 * np.exp(-(x_grid/1.0)**2)
        q_h_dis = 1.000
        status_dis = "Resonant High-Frequency Probe Approaching"
    else:
        dt = t - impact_frame
        decay_factor = np.exp(-dt / 18.0)
        core_dis = 1.2 * decay_factor * np.exp(-(x_grid/1.0)**2)
        
        # Outgoing high-frequency daughter fragments radiating outward (Jet Cones)
        x_frag1 = -v_probe * dt * 1.2
        x_frag2 = v_probe * dt * 1.2
        x_frag3 = -v_probe * dt * 0.6
        x_frag4 = v_probe * dt * 0.6
        
        frag1 = 0.35 * np.exp(-((x_grid - x_frag1)/0.5)**2) * (np.cos(6.0 * (x_grid - x_frag1))**2)
        frag2 = 0.35 * np.exp(-((x_grid - x_frag2)/0.5)**2) * (np.cos(6.0 * (x_grid - x_frag2))**2)
        frag3 = 0.20 * np.exp(-((x_grid - x_frag3)/0.6)**2) * (np.cos(4.0 * (x_grid - x_frag3))**2)
        frag4 = 0.20 * np.exp(-((x_grid - x_frag4)/0.6)**2) * (np.cos(4.0 * (x_grid - x_frag4))**2)
        
        probe_dis = frag1 + frag2 + frag3 + frag4
        q_h_dis = max(0.000, 1.000 * decay_factor)
        status_dis = "Parametric Resonance Node Unzipping (DIS Hadronization)"

    line_dis_core.set_data(x_grid, core_dis)
    line_dis_probe.set_data(x_grid, probe_dis)

    text_dis.set_text(
        f"Frame: {t}/{total_frames}\n" +
        rf"Topological Charge $Q_H$: {q_h_dis:.3f} (Unzipping to 0)" + "\n" +
        rf"Status: {status_dis}" + "\n" +
        r"Mechanic: Core Split into 6-Section Node Daughter Rings ($\omega_{\mathrm{probe}} = n\omega_{\mathrm{core}}$)"
    )

    return [line_elastic_core, line_elastic_probe, line_dis_core, line_dis_probe, text_elastic, text_dis]

# ---------------------------------------------------------
# Render Window
# ---------------------------------------------------------
plt.tight_layout()
fig.subplots_adjust(top=0.91, hspace=0.35)

anim = FuncAnimation(fig, animate, frames=total_frames, interval=1000/fps, blit=False)

plt.show()
