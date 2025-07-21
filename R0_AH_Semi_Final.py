import pybamm
import numpy as np
import matplotlib.pyplot as plt

# Load Chen2020 parameters
params = pybamm.ParameterValues("Chen2020")
rho_sei = params["SEI resistivity [Ohm.m]"]
delta_sei_0 = params["Initial SEI thickness [m]"]
electrode_area = params["Electrode width [m]"] * params["Electrode height [m]"]

# Simulation settings
cycles = 11000
cycle_numbers = np.arange(1, cycles + 1)

# SEI parameters
k_sei = 1e-9  # [m/sqrt(cycle)] - SEI growth

# LLI parameters
initial_capacity = 1.0  # Normalized (1.0 = 100%)
k_lli = 2e-4  # [fraction loss per sqrt(cycle)]

# Lithium plating parameters
k_plating_capacity = 1e-4  # capacity loss per cycle (linear)
k_plating_resistance = 2e-6  # Ohm increase per cycle

# Track values
sei_thickness = delta_sei_0 + k_sei * np.sqrt(cycle_numbers)
R0_sei = (rho_sei * sei_thickness) / electrode_area
R0_plating = k_plating_resistance * cycle_numbers
R0_total = R0_sei + R0_plating

capacity_lli = initial_capacity - k_lli * np.sqrt(cycle_numbers)
capacity_plating = initial_capacity - k_plating_capacity * cycle_numbers
capacity_total = capacity_lli + (capacity_plating - initial_capacity)

# Plotting
fig, ax = plt.subplots(1, 2, figsize=(13, 5))

# Resistance Plot
ax[0].plot(cycle_numbers, R0_sei, label="SEI Contribution")
ax[0].plot(cycle_numbers, R0_plating, label="Plating Contribution")
ax[0].plot(cycle_numbers, R0_total, label="Total $R_0$", linewidth=2)
ax[0].set_title("Internal Resistance Growth")
ax[0].set_xlabel("Cycle Number")
ax[0].set_ylabel("Resistance $R_0$ (Ω)")
ax[0].legend()
ax[0].grid(True)

# Capacity Plot
ax[1].plot(cycle_numbers, capacity_lli * 100, label="LLI Only")
ax[1].plot(cycle_numbers, capacity_plating * 100, label="Plating Only")
ax[1].plot(cycle_numbers, capacity_total * 100, label="Total Capacity", linewidth=2)
ax[1].set_title("Capacity Fade Due to LLI & Plating")
ax[1].set_xlabel("Cycle Number")
ax[1].set_ylabel("Capacity (%)")
ax[1].legend()
ax[1].grid(True)

plt.tight_layout()
plt.show()
