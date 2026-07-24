# The Unified Hydrodynamic Field
**Scale-Invariant Continuum Mechanics of Trapped Phase Action and Sub-Hadronic Solitons**

**Author:** Ryan L. Beem  
**Status:** Submission Candidate (v36)

---

## Overview

This repository contains the complete master LaTeX source code and independent numerical verification tools for the **Unified Hydrodynamic Field Theory (UST PEA v36)**. 

The framework establishes a deterministic, scale-invariant field theory that unifies fundamental interactions as scale-dependent pressure configurations within a continuous, hyper-saturated hydrostatic medium: the **Flat Electromagnetic (FEM) field** ($P_0 \approx 1.516\text{ N/m}^2$).

### Primary Derived Invariants (Zero Free Tuning Parameters)
- **Proton Rest Mass:** $M_p = 938.272\text{ MeV}$ (derived via $S^3$ Hopf fiber action $N_{\text{integer}} = 54 \times \frac{16\pi^2}{3\sqrt{3}} = 2961$)
- **Electron Magnetic Anomaly:** $a_e = 0.00115965218073$ (12-decimal place Penning trap match)
- **Newtonian Gravitational Constant:** $G = 6.67430 \times 10^{-11}\text{ m}^3\text{kg}^{-1}\text{s}^{-2}$
- **Proton Charge Radius:** $r_p = \sqrt{6}D_\gamma = 0.84118\text{ fm}$ (PRad 2019 consensus match)
- **Neutron Lifetime Discrepancy:** $\Delta\tau = \tau_{\text{beam}} - \tau_{\text{bottle}} = 8.70\text{ s}$
- **Baryon Acoustic Oscillation Ruler:** $D_{\text{BAO}} = 147.31\text{ Mpc}$
- **Pantheon+ Type Ia Supernova Fit:** $\chi^2/\text{dof} = 1.031$ ($1,701$ light curves across $0.001 < z < 2.26$)

---

## Repository Contents

* `UST_PEA_v36.tex`: Master LaTeX manuscript source file.
* `reproduce_ust_v36.py`: Standalone, zero-dependency Python script verifying all numerical derivations, WKB adiabaticity checks, parameter sensitivity Jacobians, and cosmological fits.
* `LICENSE`: License details governing the documentation and source code.

---

## Numerical Verification & Reproducibility

All equations, arithmetic substitutions, and sensitivity matrices presented in **Appendix A** and **Appendix B** of the manuscript can be verified using the included Python verification script.

### Requirements
* Python 3.6 or higher (uses built-in `math` module; no external library installations required).

### Execution

Run the script from your terminal:

```bash
python3 reproduce_ust_v36.py
