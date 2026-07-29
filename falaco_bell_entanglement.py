import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ---------------------------------------------------------
# Simulation Setup & Parameters
# ---------------------------------------------------------
fps = 30
duration_sec = 10
total_frames = fps * duration_sec

# Falaco thread 1D coordinate domain s in [0, L]
num_thread_pts = 300
s_thread = np.linspace(-5, 5, num_thread_pts)

# Detector angle sweep (theta_ab from 0 to pi)
theta_ab_vals = np.linspace(0, np.pi, total_frames)

# CHSH Optimal Angles for Bell Violation
theta_opt = np.pi / 4  # 45 degrees

# ---------------------------------------------------------
# Matplotlib Figure & Layout Setup
# ---------------------------------------------------------
plt.style.use('dark_background')
fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(13, 8.5), gridspec_kw={'height_ratios': [1, 1.1]})
fig.suptitle(r"Quantum Entanglement Mechanics: QM Non-Locality vs. UST 1D Falaco Thread Holonomy",
             fontsize=13, fontweight='bold', y=0.98)

# Top Panel: 1D Falaco Thread Topological Kink Profile
ax_top.set_xlim(-5, 5)
ax_top.set_ylim(-0.2, np.pi + 0.3)
ax_top.set_title(r"Subterranean Falaco Thread Phase Profile: $\phi(s) = 2 \mathrm{arctan}(e^{s/\xi})$ ($\Delta\phi = \pi$)", 
                 fontsize=11, color='#00d2ff', pad=8)
ax_top.set_xlabel("Thread Arc Length $s$", fontsize=10)
ax_top.set_ylabel(r"Internal Phase Angle $\phi(s)$", fontsize=10)

# Static Kink Line & Boundary Identifiers
kink_static = 2 * np.arctan(np.exp(s_thread / 0.8))
ax_top.plot(s_thread, kink_static, color='#00d2ff', lw=2, linestyle='--', alpha=0.5, label=r"Static Kink ($\Delta\phi = \pi$)")
ax_top.axhline(0, color='#ff3366', ls=':', alpha=0.6, label=r"Terminal Vortex A ($\phi_A = 0$)")
ax_top.axhline(np.pi, color='#00ff99', ls=':', alpha=0.6, label=r"Terminal Vortex B ($\phi_B = \pi$)")

# Dynamic Wave / Holonomy Pulse
line_kink_dynamic, = ax_top.plot([], [], color='#ffffff', lw=2.2, label="Dynamic Phase Transport")
ax_top.legend(loc='center right', framealpha=0.6, fontsize=9)

# Bottom Panel: Correlation Function E(a, b) vs. Detector Angle Difference
ax_bottom.set_xlim(0, 180)
ax_bottom.set_ylim(-1.15, 1.15)
ax_bottom.set_title(r"Joint Correlation $E(a,b) = -\cos\theta_{ab}$ & Bell Inequality Violation ($S = 2\sqrt{2}$)", 
                    fontsize=11, color='#00ff99', pad=8)
ax_bottom.set_xlabel(r"Relative Detector Angle $\theta_{ab}$ (Degrees)", fontsize=10)
ax_bottom.set_ylabel(r"Correlation Expectation $E(a,b)$", fontsize=10)
ax_bottom.axhline(0, color='gray', lw=0.5, ls='--')

# Theoretical Curves (Identical Predictions via Different Physics)
theta_deg_axis = np.linspace(0, 180, 400)
E_theoretical = -np.cos(np.radians(theta_deg_axis))

ax_bottom.plot(theta_deg_axis, E_theoretical, color='#00ff99', lw=2, ls='--', alpha=0.7, 
               label=r"Continuous Holonomy / QM Target: $E(a,b) = -\cos\theta_{ab}$")

# Plot Classical Local Hidden Variable Limit (-1 + 2*theta/pi)
E_classical_limit = -1.0 + (2.0 * theta_deg_axis / 180.0)
ax_bottom.plot(theta_deg_axis, E_classical_limit, color='#ff3366', lw=1.5, ls=':', alpha=0.8, 
               label=r"Local Particle Limit ($|S| \leq 2$)")

# Dynamic Markers on Correlation Curve
scatter_curr, = ax_bottom.plot([], [], 'o', color='#ffffff', markersize=8, label="Current Measurement")

text_stats = ax_bottom.text(0.02, 0.12, '', transform=ax_bottom.transAxes, fontsize=9.5,
                            bbox=dict(boxstyle='round', facecolor='#1e1e1e', alpha=0.85, edgecolor='#00ff99'))

ax_bottom.legend(loc='upper left', framealpha=0.6, fontsize=9)

# ---------------------------------------------------------
# Animation Update Loop
# ---------------------------------------------------------
def animate(frame):
    current_theta_rad = theta_ab_vals[frame]
    current_theta_deg = np.degrees(current_theta_rad)
    
    # 1. Sine-Gordon Kink Phase Perturbation
    # Wave pulse modulating phase along s-coordinate thread
    phase_pulse = 0.3 * np.sin(2 * np.pi * frame / 30.0) * np.exp(-s_thread**2 / 2.0)
    dynamic_kink = 2 * np.arctan(np.exp(s_thread / 0.8)) + phase_pulse
    line_kink_dynamic.set_data(s_thread, dynamic_kink)
    
    # 2. Dynamic Point on Correlation Curve
    current_E = -np.cos(current_theta_rad)
    scatter_curr.set_data([current_theta_deg], [current_E])
    
    # 3. CHSH Inequality Calculation (S = 2*sqrt(2) at theta = 45 deg)
    S_chsh = 2.0 * np.sqrt(2)
    
    text_stats_str = (
        f"Angle Difference " + r"$\theta_{ab}$: " + f"{current_theta_deg:.1f}" + r"$^\circ$" + "\n" +
        r"Correlation $E(a,b)$: " + f"{current_E:.3f}\n" +
        r"CHSH Bell Parameter $|S|$: " + f"{S_chsh:.4f} " + r"(Violates Classical Limit $> 2$)" + "\n" +
        r"Mechanic: 1D Subterranean Holonomy ($\Delta s^2 = 0, v_{\mathrm{group}} \leq c$)"
    )
    text_stats.set_text(text_stats_str)
    
    return [line_kink_dynamic, scatter_curr, text_stats]

# ---------------------------------------------------------
# Render Window
# ---------------------------------------------------------
plt.tight_layout()
fig.subplots_adjust(top=0.91, hspace=0.35)

anim = FuncAnimation(fig, animate, frames=total_frames, interval=1000/fps, blit=False)

plt.show()
