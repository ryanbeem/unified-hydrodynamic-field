import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ---------------------------------------------------------
# Simulation Setup & Parameters
# ---------------------------------------------------------
fps = 30
duration_sec = 8
total_frames = fps * duration_sec

x_points = 1200
x_min, x_max = -10, 10
x_eval = np.linspace(x_min, x_max, x_points)

# Comoving grid coordinates
grid_coords_base = np.arange(-8, 9, 2)

# Physics parameters
lambda_0 = 1.0          # Initial wavelength
H0_sim = 0.008          # Simulated Hubble expansion rate (Lambda-CDM)
gamma_ust = 0.08        # Spatial pitch unwinding rate (UST)
v_prop = 0.12           # Forward wave propagation velocity (c)

# ---------------------------------------------------------
# Matplotlib Figure & Layout Setup
# ---------------------------------------------------------
plt.style.use('dark_background')
fig, (ax_lcdm, ax_ust) = plt.subplots(1, 2, figsize=(15, 6.5))
fig.suptitle(r"Cosmological Redshift Mechanics: $\Lambda$CDM vs. Unified Hydrodynamic Field (UST)", 
             fontsize=14, fontweight='bold', y=0.98)

# Left Panel: Lambda-CDM Setup
ax_lcdm.set_xlim(-12, 12)
ax_lcdm.set_ylim(-2.5, 2.5)
ax_lcdm.set_title(r"Standard Model ($\Lambda$CDM): Expanding Spacetime Metric", fontsize=11, color='#ff7f0e', pad=10)
ax_lcdm.set_xlabel(r"Physical Spatial Coordinate $X(t) = a(t) \cdot x$", fontsize=10)
ax_lcdm.set_ylabel("Wave Amplitude", fontsize=10)
ax_lcdm.axhline(0, color='gray', linewidth=0.5, linestyle='--')

# Right Panel: UST UHF Setup
ax_ust.set_xlim(-12, 12)
ax_ust.set_ylim(-2.5, 2.5)
ax_ust.set_title(r"UST Field Mechanics: Static $\mathbb{R}^3$ Substrate & Pitch Unwinding", fontsize=11, color='#00d2ff', pad=10)
ax_ust.set_xlabel(r"Euclidean Spatial Coordinate $x$ (Unwarped Flat Space)", fontsize=10)
ax_ust.set_ylabel("Transverse Fluid Shear Amplitude", fontsize=10)
ax_ust.axhline(0, color='gray', linewidth=0.5, linestyle='--')

# Initialize Line Objects
wave_line_lcdm, = ax_lcdm.plot([], [], color='#ff7f0e', lw=2, label="Stretching Wave Envelope")
wave_line_ust, = ax_ust.plot([], [], color='#00d2ff', lw=2, label="Unwinding Helical Shear")

# Storage for dynamic grid lines and text annotations
grid_lines_lcdm = [ax_lcdm.axvline(0, color='#ff7f0e', alpha=0.3, ls=':') for _ in grid_coords_base]
grid_lines_ust = [ax_ust.axvline(x, color='#00d2ff', alpha=0.3, ls=':') for x in grid_coords_base]

text_lcdm = ax_lcdm.text(0.03, 0.88, '', transform=ax_lcdm.transAxes, fontsize=9,
                         bbox=dict(boxstyle='round', facecolor='#1e1e1e', alpha=0.8, edgecolor='#ff7f0e'))

text_ust = ax_ust.text(0.03, 0.88, '', transform=ax_ust.transAxes, fontsize=9,
                       bbox=dict(boxstyle='round', facecolor='#1e1e1e', alpha=0.8, edgecolor='#00d2ff'))

ax_lcdm.legend(loc='lower right', framealpha=0.5)
ax_ust.legend(loc='lower right', framealpha=0.5)

# ---------------------------------------------------------
# Animation Frame Update Function
# ---------------------------------------------------------
def animate(frame):
    t = frame
    
    # =====================================================
    # 1. Lambda-CDM Dynamics (Expanding Metric)
    # =====================================================
    a_t = 1.0 + H0_sim * t  # Scale factor a(t)
    
    # Update expanding grid lines
    for line, x_base in zip(grid_lines_lcdm, grid_coords_base):
        line.set_xdata([x_base * a_t, x_base * a_t])
        
    # Wave packet center propagating on expanding background
    x_center_lcdm = -8.0 * a_t + v_prop * t * a_t
    
    # Wave profile: Wavelength stretches with scale factor a(t)
    lambda_lcdm = lambda_0 * a_t
    k_lcdm = 2 * np.pi / lambda_lcdm
    envelope_lcdm = np.exp(-((x_eval - x_center_lcdm) / (1.5 * a_t))**2)
    y_lcdm = envelope_lcdm * np.sin(k_lcdm * (x_eval - x_center_lcdm))
    
    wave_line_lcdm.set_data(x_eval, y_lcdm)
    
    z_lcdm = a_t - 1.0
    text_lcdm.set_text(
        rf"Scale Factor $a(t)$: {a_t:.3f}" + "\n" +
        rf"Redshift $z$: {z_lcdm:.3f}" + "\n" +
        rf"Metric: Expanding ($g_{{xx}} \propto a^2(t)$)" + "\n" +
        rf"Energy Source: Dark Energy ($\Omega_\Lambda \approx 0.7$)"
    )

    # =====================================================
    # 2. UST Field Dynamics (Static Substrate Pitch Unwinding)
    # =====================================================
    # Wave packet center propagating across static Euclidean grid at c
    x_center_ust = -8.0 + v_prop * t
    
    # Distance traversed through medium
    dist_traversed = np.maximum(0, x_eval - (-8.0))
    
    # Local wavelength unwinds along propagation trajectory: \lambda(x) = \lambda_0 (1 + \gamma x)
    lambda_ust_x = lambda_0 * (1.0 + gamma_ust * dist_traversed)
    
    # Phase integral \Phi(x) = \int (2\pi / \lambda(x)) dx
    phase_ust = (2 * np.pi / (gamma_ust * lambda_0)) * np.log(1.0 + gamma_ust * dist_traversed)
    
    # Transverse shear amplitude unwinds into background longitudinal mode
    amplitude_ust = 1.0 / np.sqrt(1.0 + gamma_ust * dist_traversed)
    
    envelope_ust = np.exp(-((x_eval - x_center_ust) / 1.5)**2)
    y_ust = envelope_ust * amplitude_ust * np.sin(phase_ust - (2 * np.pi / lambda_0) * (v_prop * t))
    
    wave_line_ust.set_data(x_eval, y_ust)
    
    # Effective cosmological redshift at current packet position
    z_ust = gamma_ust * np.maximum(0, x_center_ust - (-8.0))
    text_ust.set_text(
        rf"Substrate Grid: Static $\mathbb{{R}}^3$ (0.00% Expansion)" + "\n" +
        rf"Effective Redshift $z$: {z_ust:.3f}" + "\n" +
        rf"Mechanic: Transverse Pitch Unwinding ($\gamma x$)" + "\n" +
        rf"Luminosity Distance: $d_L(z) = \frac{{c}}{{H_0}}(1+z)\ln(1+z)$"
    )

    return [wave_line_lcdm, wave_line_ust, text_lcdm, text_ust] + grid_lines_lcdm

# ---------------------------------------------------------
# Render & Display
# ---------------------------------------------------------
plt.tight_layout()
fig.subplots_adjust(top=0.88)

anim = FuncAnimation(fig, animate, frames=total_frames, interval=1000/fps, blit=False)

plt.show()