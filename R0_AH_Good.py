import pybamm 
import numpy as np
import matplotlib.pyplot as plt

# Load Chen2020 parameters
params = pybamm.ParameterValues("Chen2020")
rho_sei = params["SEI resistivity [Ohm.m]"]
delta_sei_0 = params["Initial SEI thickness [m]"]
electrode_area = params["Electrode width [m]"] * params["Electrode height [m]"]

# Simulation settings
cycles = 1200
cycle_numbers = np.arange(1, cycles + 1)

# Degradation constants
initial_capacity_ah = 5.0  # in Ah, assuming initial capacity is 5Ah
k_sei = 1e-9  # [m/sqrt(cycle)]
k_lli = 2e-4 * initial_capacity_ah  # Ah loss per sqrt(cycle)
k_plating_capacity = 1e-4 * initial_capacity_ah  # Ah loss per cycle
k_crack = 1e-5 * initial_capacity_ah  # Ah loss per cycle
k_lam = 5e-5 * initial_capacity_ah  # Ah loss per cycle

# Resistance growth rates
k_plating_resistance = 2e-6  # Ohm per cycle
k_crack_resistance = 1e-6  # Ohm per cycle
k_lam_resistance = 0.5e-6  # Ohm per cycle
k_lli_resistance = 1e-6  # small resistance growth due to loss of active Li

# Individual degradation contributions
sei_thickness = delta_sei_0 + k_sei * np.sqrt(cycle_numbers)
R0_sei = (rho_sei * sei_thickness) / electrode_area
R0_plating = k_plating_resistance * cycle_numbers
R0_crack = k_crack_resistance * cycle_numbers
R0_lam = k_lam_resistance * cycle_numbers
R0_lli = k_lli_resistance * np.sqrt(cycle_numbers)

R0_total = R0_sei + R0_plating + R0_crack + R0_lam + R0_lli

# Capacity degradation
capacity_lli = initial_capacity_ah - k_lli * np.sqrt(cycle_numbers)
capacity_plating = initial_capacity_ah - k_plating_capacity * cycle_numbers
capacity_crack = initial_capacity_ah - k_crack * cycle_numbers
capacity_lam = initial_capacity_ah - k_lam * cycle_numbers

# Total capacity loss (assuming additive losses)
capacity_total = capacity_lli + (capacity_plating - initial_capacity_ah) \
                 + (capacity_crack - initial_capacity_ah) + (capacity_lam - initial_capacity_ah)

# Plotting
fig, ax = plt.subplots(1, 2, figsize=(14, 6))

# Resistance Plot
ax[0].plot(cycle_numbers, R0_sei, label="SEI")
ax[0].plot(cycle_numbers, R0_plating, label="Li Plating")
ax[0].plot(cycle_numbers, R0_crack, label="Particle Cracking")
ax[0].plot(cycle_numbers, R0_lam, label="LAM")
ax[0].plot(cycle_numbers, R0_lli, label="LLI")
ax[0].plot(cycle_numbers, R0_total, label="Total $R_0$", linewidth=2.5)
ax[0].set_title("Internal Resistance Growth", fontsize=14)
ax[0].set_xlabel("Cycle Number", fontsize=14)
ax[0].set_ylabel("Resistance $R_0$ (Ω)", fontsize=14)
ax[0].legend()
ax[0].grid(True)

# Capacity Plot
ax[1].plot(cycle_numbers, capacity_lli, label="LLI")
ax[1].plot(cycle_numbers, capacity_plating, label="Li Plating")
ax[1].plot(cycle_numbers, capacity_crack, label="Particle Cracking")
ax[1].plot(cycle_numbers, capacity_lam, label="LAM")
ax[1].plot(cycle_numbers, capacity_total, label="Total Capacity", linewidth=3)
ax[1].set_title("Capacity Fade (Ah) over Cycles", fontsize=14)
ax[1].set_xlabel("Cycle Number", fontsize=14)
ax[1].set_ylabel("Capacity (Ah)", fontsize=14)
ax[1].legend()
ax[1].grid(True)

plt.tight_layout()
plt.show()
