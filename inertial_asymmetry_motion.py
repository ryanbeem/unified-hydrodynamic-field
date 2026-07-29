import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ---------------------------------------------------------
# Simulation Setup & Parameters
# ---------------------------------------------------------
fps = 30
total_frames = 270

x_pts = 1000
x_grid = np.linspace(-12, 12, x_pts)

# Physical parameters
k0 = 2.5             # Rest internal wavenumber
v_max = 0.10         # Terminal velocity after impact
soliton_width = 1.2  # Envelope width

# Phase timelines (Frames)
t_impact1_start = 25
t_impact1_hit = 55
t_impact2_start = 180
t_impact2_hit = 210

# ---------------------------------------------------------
# Matplotlib Layout Setup
# ---------------------------------------------------------
plt.style.use('dark_background')
fig, (ax_top, ax_bottom) = plt.subplots(2, 1, figsize=(13, 8.5), gridspec_kw={'height_ratios': [1.2, 1]})
fig.suptitle(r"UST Inertial Mechanics: Kinetic Impact $\to$ Internal Wave Asymmetry $\to$ Self-Sustained Motion", 
             fontsize=13, fontweight='bold', y=0.98)

# Top Panel: Soliton Field Envelope & Impact Pulses
ax_top.set_xlim(-12, 12)
ax_top.set_ylim(-1.5, 2.2)
ax_top.set_title(r"Soliton Envelope & Internal Phase: Rest ($v=0$) vs. Moving Asymmetric State ($v > 0$)", 
                 fontsize=11, color='#00d2ff', pad=8)
ax_top.set_ylabel("Field Amplitude", fontsize=10)
ax_top.axhline(0, color='gray', lw=0.5, ls='--')

line_core_env, = ax_top.plot([], [], color='#00d2ff', lw=2.2, label=r"Soliton Envelope ($Q_H=1$)")
line_core_internal, = ax_top.plot([], [], color='#ffffff', lw=1.0, alpha=0.8, label="Internal Phase Oscillation")
line_pulse_L, = ax_top.plot([], [], color='#ff7f0e', lw=1.8, ls='--', label="Left Kinetic Impact Pulse")
line_pulse_R, = ax_top.plot([], [], color='#ff3366', lw=1.8, ls='--', label="Right Counter Impact Pulse")

text_phase = ax_top.text(0.02, 0.72, '', transform=ax_top.transAxes, fontsize=9.5,
                          bbox=dict(boxstyle='round', facecolor='#1e1e1e', alpha=0.85, edgecolor='#00d2ff'))
ax_top.legend(loc='upper right', framealpha=0.6, fontsize=9)

# Bottom Panel: Pressure Gradient / Asymmetry Profile
ax_bottom.set_xlim(-12, 12)
ax_bottom.set_ylim(-0.2, 1.2)
ax_bottom.set_title(r"Internal Pressure Gradient / Wavenumber Asymmetry $\Delta k(x)$ (Drives Motion)", 
                    fontsize=11, color='#00ff99', pad=8)
ax_bottom.set_xlabel("Substrate Spatial Axis $x$", fontsize=10)
ax_bottom.set_ylabel("Internal Pressure Asymmetry", fontsize=10)
ax_bottom.axhline(0, color='gray', lw=0.5, ls='--')

line_asym, = ax_bottom.plot([], [], color='#00ff99', lw=2.0, label=r"Pressure Imbalance $\Delta P(x)$")
scatter_centroid, = ax_bottom.plot([], [], 'o', color='#00ff99', markersize=8, label="Soliton Centroid")

text_stats = ax_bottom.text(0.02, 0.65, '', transform=ax_bottom.transAxes, fontsize=9.5,
                            bbox=dict(boxstyle='round', facecolor='#1e1e1e', alpha=0.85, edgecolor='#00ff99'))
ax_bottom.legend(loc='upper right', framealpha=0.6, fontsize=9)

# ---------------------------------------------------------
# Dynamic Kinematics & Wave Calculations
# ---------------------------------------------------------
def animate(frame):
    t = frame
    
    # 1. Calculate Soliton Velocity v(t) & Position x_c(t)
    if t < t_impact1_hit:
        # Initial Rest State or Accelerating during Impact 1
        if t < t_impact1_start:
            v = 0.0
            x_c = -5.0
            stage_str = "1. Rest State (Symmetric Standing Wave, v = 0)"
        else:
            progress = (t - t_impact1_start) / (t_impact1_hit - t_impact1_start)
            v = v_max * progress
            x_c = -5.0 + 0.5 * v_max * (t - t_impact1_start) * progress
            stage_str = "2. Left Kinetic Impact (Creating Phase Asymmetry)"
    elif t_impact1_hit <= t < t_impact2_start:
        # Sustained Inertial Motion
        v = v_max
        dt = t - t_impact1_hit
        x_c = -5.0 + (v_max * (t_impact1_hit - t_impact1_start) * 0.5) + v_max * dt
        stage_str = "3. Sustained Inertial Motion (Asymmetry Maintains Motion, v > 0)"
    elif t_impact2_start <= t < t_impact2_hit:
        # Decelerating during Counter Impact
        progress = (t - t_impact2_start) / (t_impact2_hit - t_impact2_start)
        v = v_max * (1.0 - progress)
        dt_base = t_impact2_start - t_impact1_hit
        x_c_base = -5.0 + (v_max * (t_impact1_hit - t_impact1_start) * 0.5) + v_max * dt_base
        x_c = x_c_base + v_max * (t - t_impact2_start) * (1.0 - 0.5 * progress)
        stage_str = "4. Counter Kinetic Impact (Restoring Internal Symmetry)"
    else:
        # Final Restored Rest State
        v = 0.0
        dt_base = t_impact2_start - t_impact1_hit
        dt_decel = t_impact2_hit - t_impact2_start
        x_c = -5.0 + (v_max * (t_impact1_hit - t_impact1_start) * 0.5) + v_max * dt_base + 0.5 * v_max * dt_decel
        stage_str = "5. Restored Rest State (Symmetry Restored, v = 0)"

    # 2. Compute Soliton Envelope & Doppler-Shifted Internal Wave
    # Asymmetric wavenumber: Compressed ahead (k_front), stretched behind (k_back)
    k_local = k0 * (1.0 + 2.5 * v * np.tanh((x_grid - x_c) / soliton_width))
    phase_integral = k0 * (x_grid - x_c) + 2.5 * v * k0 * soliton_width * np.log(np.cosh((x_grid - x_c) / soliton_width))
    
    # Skewed Asymmetric Envelope during Motion
    skew_factor = 1.0 - 0.8 * v * np.tanh((x_grid - x_c) / soliton_width)
    envelope = np.exp(-((x_grid - x_c) / soliton_width)**2 * skew_factor)
    internal_wave = envelope * np.sin(phase_integral - 2.0 * t)
    
    line_core_env.set_data(x_grid, envelope)
    line_core_internal.set_data(x_grid, internal_wave)

    # 3. Compute Impact Pulses
    # Left Impact Pulse
    if t < t_impact1_hit:
        x_pL = -11.0 + (x_c - (-11.0)) * (t / t_impact1_hit)
        pulse_L = 0.7 * np.exp(-((x_grid - x_pL)/0.8)**2) * np.sin(4.0 * (x_grid - x_pL))
    else:
        pulse_L = np.zeros_like(x_grid)
        
    # Right Counter Pulse
    if t >= t_impact2_start and t < t_impact2_hit:
        x_pR = 11.0 - (11.0 - x_c) * ((t - t_impact2_start) / (t_impact2_hit - t_impact2_start))
        pulse_R = 0.7 * np.exp(-((x_grid - x_pR)/0.8)**2) * np.sin(4.0 * (x_grid - x_pR))
    else:
        pulse_R = np.zeros_like(x_grid)

    line_pulse_L.set_data(x_grid, pulse_L)
    line_pulse_R.set_data(x_grid, pulse_R)

    # 4. Asymmetry Profile (Bottom Panel)
    asymmetry_profile = envelope * (k_local - k0) / k0
    line_asym.set_data(x_grid, asymmetry_profile)
    scatter_centroid.set_data([x_c], [0.0])

    # Update Text Statuses
    text_phase.set_text(
        f"Frame: {t}/{total_frames}\n" +
        f"Soliton Position $x_c$: {x_c:.2f}\n" +
        f"Soliton Velocity $v$: {v:.3f} c\n" +
        f"Current Phase: {stage_str}"
    )

    text_stats.set_text(
        f"Velocity $v$: {v:.3f}\n" +
        rf"Internal Pressure Imbalance $\Delta P$: {np.max(np.abs(asymmetry_profile)):.3f}" + "\n" +
        r"Mechanic: Net Pressure Imbalance Drives Continuous Drift Through $\mathbb{R}^3$"
    )

    return [line_core_env, line_core_internal, line_pulse_L, line_pulse_R, line_asym, scatter_centroid]

# ---------------------------------------------------------
# Render Window
# ---------------------------------------------------------
plt.tight_layout()
fig.subplots_adjust(top=0.91, hspace=0.35)

anim = FuncAnimation(fig, animate, frames=total_frames, interval=1000/fps, blit=False)

plt.show()
