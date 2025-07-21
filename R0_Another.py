import pybamm
import numpy as np
import matplotlib.pyplot as plt

# Define the battery model with SEI growth (reaction-limited)
model = pybamm.lithium_ion.DFN(
    options={
        "SEI": "reaction limited",
        "SEI film resistance": "distributed",
    }
)

# Load default parameter set (Chen2020 for LG M50 cell)
param = pybamm.ParameterValues("Chen2020")

# Define cycling experiment
experiment = pybamm.Experiment([
    ("Charge at 1C until 4.2 V", "Hold at 4.2 V until C/20"),
    ("Rest for 10 minutes"),
    ("Discharge at 1C until 2.5 V"),
    ("Rest for 10 minutes"),
] * 50)  # Repeat for 50 cycles

# Create and solve simulation
sim = pybamm.Simulation(model, parameter_values=param, experiment=experiment)
solution = sim.solve()

# Extract internal resistance from simulation results
time = solution["Time [h]"].entries
current = solution["Current [A]"].entries
terminal_voltage = solution["Terminal voltage [V]"].entries
ocv = 5 V

# Avoid calculating resistance during rest periods (when current is near zero)
epsilon = 1e-6  # Small threshold to avoid division by zero
safe_current = np.where(np.abs(current) < epsilon, np.nan, current)  # Set rest periods to NaN

# Calculate internal resistance (Ohm's law: R_internal = (OCV - V_terminal) / Current)
internal_resistance = np.abs((ocv - terminal_voltage) / safe_current)

# Replace NaN values with an appropriate replacement (e.g., interpolate or fill)
internal_resistance = np.nan_to_num(internal_resistance, nan=np.nanmedian(internal_resistance))

# Plot internal resistance growth over time
plt.figure(figsize=(8,5))
plt.plot(time, internal_resistance * 1000)  # Convert to milliohms (mΩ)
plt.xlabel("Time [hours]")
plt.ylabel("Internal Resistance [mΩ]")
plt.title("Internal Resistance Growth due to SEI Formation")
plt.grid(True)
plt.show()

