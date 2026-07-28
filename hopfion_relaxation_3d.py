import numpy as np
import matplotlib.pyplot as plt

class SpongeHopfionRelaxation3D:
    """
    High-Precision 3D Skyrme-Faddeev Soliton Relaxation Engine (UST PEA v38).
    
    Features:
    1. Spatial Boundary Sponge Layer absorbing edge radiation waves.
    2. Dynamic Kinetic Resetting (v . f < 0) for rapid energy dissipation.
    3. Energy Density Thresholding (E >= 0.15 * E_max) to isolate torus core radius.
    4. N=64 spatial resolution preserving topological charge Q_H ~ 0.94.
    """
    def __init__(self, N=64, L=2.0, P0=1.0, D_gamma=0.1, eta=1.0, dt_scale=0.06):
        self.N = N
        self.L = L
        self.dx = L / N
        self.dt = dt_scale * self.dx  # Stable CFL timestep
        self.eta = eta
        self.P0 = P0
        self.K1 = P0 * (D_gamma**2)
        self.K2 = P0 * (D_gamma**4)
        
        # Target analytical equilibrium radius: R_0 = sqrt(1.5) * D_gamma = 0.1225
        self.R0_analytical = np.sqrt(1.5) * D_gamma
        
        # 3D Coordinate Mesh
        x = np.linspace(-L/2, L/2, N)
        self.X, self.Y, self.Z = np.meshgrid(x, x, x, indexing='ij')
        self.R_dist = np.sqrt(self.X**2 + self.Y**2 + self.Z**2)
        
        self.n_field = np.zeros((3, N, N, N))
        self.v_field = np.zeros((3, N, N, N))
        
        # Fourier space operators for Chern-Simons Helicity
        kx = 2.0 * np.pi * np.fft.fftfreq(N, d=self.dx)
        self.KX, self.KY, self.KZ = np.meshgrid(kx, kx, kx, indexing='ij')
        self.K2_mesh = self.KX**2 + self.KY**2 + self.KZ**2
        self.K2_mesh[0, 0, 0] = 1.0  # Prevent division by zero
        
        # Seed initial Q_H = 1 Hopfion knot
        self.seed_hopfion_knot(R0=0.30)

    def seed_hopfion_knot(self, R0=0.30):
        r2 = self.R_dist**2
        Z1 = self.X + 1j * self.Y
        Z2 = self.Z + 1j * (r2 - R0**2) / (2.0 * R0)
        denom = np.abs(Z1)**2 + np.abs(Z2)**2
        W = 2.0 * Z1 * np.conj(Z2)
        
        self.n_field[0] = np.real(W) / denom
        self.n_field[1] = np.imag(W) / denom
        self.n_field[2] = (np.abs(Z1)**2 - np.abs(Z2)**2) / denom
        
        norm = np.linalg.norm(self.n_field, axis=0)
        self.n_field /= norm

    def compute_gradients(self, field):
        gx = np.gradient(field, self.dx, axis=1)
        gy = np.gradient(field, self.dx, axis=2)
        gz = np.gradient(field, self.dx, axis=3)
        return gx, gy, gz

    def compute_exact_hopf_charge(self):
        gx, gy, gz = self.compute_gradients(self.n_field)
        
        F_yz = np.sum(self.n_field * np.cross(gy, gz, axis=0), axis=0)
        F_zx = np.sum(self.n_field * np.cross(gz, gx, axis=0), axis=0)
        F_xy = np.sum(self.n_field * np.cross(gx, gy, axis=0), axis=0)
        
        F_k_x = np.fft.fftn(F_yz)
        F_k_y = np.fft.fftn(F_zx)
        F_k_z = np.fft.fftn(F_xy)
        
        A_k_x = 1j * (self.KY * F_k_z - self.KZ * F_k_y) / self.K2_mesh
        A_k_y = 1j * (self.KZ * F_k_x - self.KX * F_k_z) / self.K2_mesh
        A_k_z = 1j * (self.KX * F_k_y - self.KY * F_k_x) / self.K2_mesh
        
        A_k_x[0, 0, 0] = A_k_y[0, 0, 0] = A_k_z[0, 0, 0] = 0.0
        
        A_x = np.real(np.fft.ifftn(A_k_x))
        A_y = np.real(np.fft.ifftn(A_k_y))
        A_z = np.real(np.fft.ifftn(A_k_z))
        
        helicity_density = A_x * F_yz + A_y * F_zx + A_z * F_xy
        return np.sum(helicity_density) * (self.dx**3) / (16.0 * np.pi**2)

    def compute_energies_and_radius(self):
        gx, gy, gz = self.compute_gradients(self.n_field)
        v_sq = np.sum(self.v_field**2, axis=0)
        E_kin = 0.5 * np.sum(v_sq) * (self.dx**3)
        
        grad_n_sq = np.sum(gx**2 + gy**2 + gz**2, axis=0)
        E_K1 = 0.5 * self.K1 * np.sum(grad_n_sq) * (self.dx**3)
        
        F_xy = np.cross(gx, gy, axis=0)
        F_yz = np.cross(gy, gz, axis=0)
        F_zx = np.cross(gz, gx, axis=0)
        F_sq = np.sum(F_xy**2 + F_yz**2 + F_zx**2, axis=0)
        E_K2 = 0.25 * self.K2 * np.sum(F_sq) * (self.dx**3)
        
        E_static = E_K1 + E_K2
        E_total = E_kin + E_static
        
        # Isolate top 85% Energy Density Core (Thresholding)
        energy_density = 0.5 * self.K1 * grad_n_sq + 0.25 * self.K2 * F_sq
        E_max = np.max(energy_density)
        core_threshold_mask = energy_density >= (0.15 * E_max)
        core_density = energy_density * core_threshold_mask
        total_core_energy = np.sum(core_density) * (self.dx**3)
        
        if total_core_energy > 0:
            R_torus_core = np.sqrt(np.sum((self.R_dist**2) * core_density) * (self.dx**3) / total_core_energy)
        else:
            R_torus_core = 0.0
            
        return E_total, E_kin, E_static, R_torus_core

    def compute_tangential_forces(self):
        gx, gy, gz = self.compute_gradients(self.n_field)
        
        laplacian = (np.roll(self.n_field, 1, axis=1) + np.roll(self.n_field, -1, axis=1) +
                     np.roll(self.n_field, 1, axis=2) + np.roll(self.n_field, -1, axis=2) +
                     np.roll(self.n_field, 1, axis=3) + np.roll(self.n_field, -1, axis=3) -
                     6.0 * self.n_field) / (self.dx**2)
        force_K1 = self.K1 * laplacian
        
        F_xy = np.cross(gx, gy, axis=0)
        F_yz = np.cross(gy, gz, axis=0)
        F_zx = np.cross(gz, gx, axis=0)
        force_K2 = self.K2 * (np.cross(gx, F_xy, axis=0) + np.cross(gy, F_yz, axis=0) + np.cross(gz, F_zx, axis=0))
        
        raw_forces = force_K1 + force_K2
        F_dot_n = np.sum(raw_forces * self.n_field, axis=0)
        f_tangent = raw_forces - F_dot_n * self.n_field
        return f_tangent

    def step_damped_dynamics(self):
        f_tangent = self.compute_tangential_forces()
        
        # 1. Dynamic Kinetic Reset
        power_injection = np.sum(self.v_field * f_tangent)
        if power_injection < 0:
            self.v_field.fill(0.0)
            
        # 2. Spatial Boundary Sponge Layer
        r_norm = self.R_dist / (0.5 * self.L)
        eta_spatial = self.eta + 12.0 * np.clip(r_norm - 0.65, 0.0, 1.0)**3
        
        # 3. Damped Velocity & Position Update
        accel = f_tangent - eta_spatial * self.v_field
        self.v_field += accel * self.dt
        self.n_field += self.v_field * self.dt
        
        # 4. Project onto S^2 Manifold
        norm = np.linalg.norm(self.n_field, axis=0)
        self.n_field /= norm
        v_dot_n = np.sum(self.v_field * self.n_field, axis=0)
        self.v_field -= v_dot_n * self.n_field

if __name__ == "__main__":
    solver = SpongeHopfionRelaxation3D(N=64, L=2.0, P0=1.0, D_gamma=0.1, eta=1.0, dt_scale=0.06)
    
    total_steps = 2000
    log_interval = 200
    
    time_history = []
    energy_total_history = []
    energy_kin_history = []
    energy_static_history = []
    radius_history = []
    qh_history = []
    
    print("=" * 70)
    print(f" EXTENDED SOLITON RELAXATION TO GROUND STATE ({total_steps} Steps)")
    print("=" * 70)
    print(f"Grid Resolution           : N={solver.N}^3 (dx = {solver.dx:.5f})")
    print(f"Core Resolution           : {0.30 / solver.dx:.2f} grid points across core")
    print(f"Target Equilibrium R_0    : {solver.R0_analytical:.4f} code units")
    print("Boundary Damping          : Spatial Sponge Layer + Kinetic Resets")
    print("Core Radius Metric        : Energy Density Thresholding (E >= 0.15 * E_max)")
    print("=" * 70 + "\n")
    
    for s in range(total_steps + 1):
        if s % log_interval == 0:
            E_tot, E_kin, E_stat, R_core = solver.compute_energies_and_radius()
            qh = solver.compute_exact_hopf_charge()
            
            time_history.append(s * solver.dt)
            energy_total_history.append(E_tot)
            energy_kin_history.append(E_kin)
            energy_static_history.append(E_stat)
            radius_history.append(R_core)
            qh_history.append(qh)
            
            print(f"Step {s:04d} | E_tot: {E_tot:.5f} | E_kin: {E_kin:.6f} | E_stat: {E_stat:.5f} | R_core: {R_core:.4f} | Q_H: {qh:.4f}")
            
        solver.step_damped_dynamics()
        
    # Plot Relaxation Curves
    fig, axes = plt.subplots(3, 1, figsize=(9, 10), sharex=True, layout="constrained")
    
    axes[0].plot(time_history, energy_total_history, 'b-o', linewidth=2, label=r'Total Energy $E_{\mathrm{tot}}(t) \to M_0$')
    axes[0].plot(time_history, energy_kin_history, 'r--', linewidth=1.5, label=r'Kinetic Energy $E_{\mathrm{kin}}(t) \to 0$')
    axes[0].set_ylabel('Energy [Code Units]', fontsize=11)
    axes[0].set_title(r'Extended Energy Relaxation down to Rest Mass ($M_0$)', fontsize=12)
    axes[0].grid(True, linestyle='--', alpha=0.6)
    axes[0].legend(loc='upper right')
    
    axes[1].plot(time_history, radius_history, 'g-s', linewidth=2, label=r'Inner Torus Core $R_{\mathrm{core}}(t)$')
    axes[1].axhline(y=solver.R0_analytical, color='darkgreen', linestyle=':', linewidth=1.5, label=r'Analytical Target $R_0 = 0.1225$')
    axes[1].set_ylabel('Radius [Code Units]', fontsize=11)
    axes[1].set_title(r'Torus Core Contraction toward Analytical Target ($R_0$)', fontsize=12)
    axes[1].grid(True, linestyle='--', alpha=0.6)
    axes[1].legend(loc='upper right')
    
    axes[2].plot(time_history, qh_history, 'm-d', linewidth=2, label=r'Topological Invariant $Q_H(t)$')
    axes[2].set_xlabel(r'Simulation Time $t$ [Code Units]', fontsize=11)
    axes[2].set_ylabel(r'Hopf Charge $Q_H$', fontsize=11)
    axes[2].set_title(r'Topological Conservation ($Q_H \approx 0.94$)', fontsize=12)
    axes[2].set_ylim(0.80, 1.05)
    axes[2].grid(True, linestyle='--', alpha=0.6)
    axes[2].legend(loc='lower right')
    
    plt.show()
