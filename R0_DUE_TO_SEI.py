import pybamm
import numpy as np
import matplotlib.pyplot as plt

# Load parameters from Chen2020 model
params = pybamm.ParameterValues("Chen2020")

# Parameters
rho_sei = params["SEI resistivity [Ohm.m]"]
delta_sei_0 = params["Initial SEI thickness [m]"]  # SEI thickness at cycle 0
electrode_area = params["Electrode width [m]"] * params["Electrode height [m]"]  # m²

# Simulation parameters
cycles = 1200
k = 1e-11  # SEI growth constant (m / sqrt(cycle)), assumed based on literature

# Arrays
cycle_numbers = np.arange(1, cycles + 1)
sei_thicknesses = delta_sei_0 + k * np.sqrt(cycle_numbers)
R0_values = (rho_sei * sei_thicknesses) / electrode_area

# Plot
plt.figure(figsize=(8, 5))
plt.plot(cycle_numbers, R0_values, lw=3)
plt.xlabel("Cycle Number", fontsize=20)
plt.ylabel("Internal Resistance $R_0$ (Ω)", fontsize=20)
plt.grid(True)
plt.tight_layout()
plt.show()
