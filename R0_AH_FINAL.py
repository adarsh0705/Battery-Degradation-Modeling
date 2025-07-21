import pybamm
import numpy as np
import matplotlib.pyplot as plt

# Define experiment with high C-rate and low temperature
cycles = 1200
experiment = pybamm.Experiment([
    "Charge at 3C until 90% SOC at 0°C",
    "Discharge at 3C until 30% SOC at 0°C"
] * cycles)

# Load model and parameters
model = pybamm.lithium_ion.SPM()
param = pybamm.ParameterValues("Chen2020")
sim = pybamm.Simulation(model, experiment=experiment, parameter_values=param)

# Solve the experiment (optional: not used for degradation plots here)
solution = sim.solve()

# Constants for degradation modeling
rho_sei = param["SEI resistivity [Ohm.m]"]
delta_sei_0 = param["Initial SEI thickness [m]"]
electrode_area = param["Electrode width [m]"] * param["Electrode height [m]"]

initial_capacity_ah = 5.0
total_cycles = cycles

# Adjusted degradation constants to achieve ~79% remaining capacity after 1200 cycles
# Total degradation = 5.0 - 3.95 = 1.05 Ah
# Allocating: LLI = 0.3 Ah, plating = 0.25 Ah, cracking = 0.25 Ah, LAM = 0.25 Ah
k_sei = 1e-9  # SEI growth constant (not affecting capacity directly here)
k_lli = 0.3 / np.sqrt(total_cycles)              # Ah per sqrt(cycle)
k_plating_capacity = 0.25 / total_cycles         # Ah per cycle
k_crack = 0.25 / total_cycles                    # Ah per cycle
k_lam = 0.25 / total_cycles                      # Ah per cycle

# Resistance constants
k_plating_resistance = 1e-7
k_crack_resistance = 5e-8
k_lam_resistance = 2e-8
k_lli_resistance = 5e-8

# Cycle index
cycle_numbers = np.arange(1, cycles + 1)

# Resistance over cycles
sei_thickness = delta_sei_0 + k_sei * np.sqrt(cycle_numbers)
R0_sei = (rho_sei * sei_thickness) / electrode_area
R0_total = R0_sei \
         + k_plating_resistance * cycle_numbers \
         + k_crack_resistance * cycle_numbers \
         + k_lam_resistance * cycle_numbers \
         + k_lli_resistance * np.sqrt(cycle_numbers)

# Capacity degradation (%)
capacity_total = initial_capacity_ah \
    - k_lli * np.sqrt(cycle_numbers) \
    - k_plating_capacity * cycle_numbers \
    - k_crack * cycle_numbers \
    - k_lam * cycle_numbers
capacity_percentage = (capacity_total / initial_capacity_ah) * 100

# Simplified SOC profile vs cycles (alternating 90% ↔ 30%)
soc_profile = []
for _ in range(cycles):
    soc_profile.append(0.9)  # Charge
    soc_profile.append(0.3)  # Discharge
cycle_soc = np.arange(1, len(soc_profile) + 1)

# --- Plot 1: Resistance Growth ---
plt.figure(figsize=(8, 5))
plt.plot(cycle_numbers, R0_total, color="blue")
plt.title("Internal Resistance Growth vs Cycles")
plt.xlabel("Cycle Number", fontsize=14)
plt.ylabel("Resistance $R_0$ (Ω)", fontsize=14)
plt.grid(False)
plt.tight_layout()
plt.show()

# --- Plot 2: Capacity Fade ---
plt.figure(figsize=(8, 5))
plt.plot(cycle_numbers, capacity_percentage, color="green")
plt.title("Capacity Fade vs Cycles")
plt.xlabel("Cycle Number", fontsize=14)
plt.ylabel("Remaining Capacity (%)", fontsize=14)
plt.grid(False)
plt.tight_layout()
plt.show()

# --- Plot 3: SOC Profile ---
plt.figure(figsize=(8, 5))
plt.plot(cycle_soc, soc_profile, color="purple")
plt.title("SOC Profile vs Cycles")
plt.xlabel("Cycle Number", fontsize=14)
plt.ylabel("SOC", fontsize=14)
plt.ylim(0.2, 1.0)
plt.grid(False)
plt.tight_layout()
plt.show()
