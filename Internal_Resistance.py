import pybamm
import matplotlib.pyplot as plt
import numpy as np  # Import numpy for linspace

# Load the default DFN (Doyle-Fuller-Newman) model
model = pybamm.lithium_ion.DFN()

# Define parameters using a built-in parameter set (e.g., Marquis2019)
parameter_values = pybamm.ParameterValues("Marquis2019")

# Set up the simulation
simulation = pybamm.Simulation(model, parameter_values=parameter_values)

# Solve the simulation for a specified time span (e.g., 1 hour = 3600 seconds)
t_eval = np.linspace(0, 3600, 1000)  # Use numpy.linspace for time steps
solution = simulation.solve(t_eval)

# Extract internal resistance from the solution
# PyBaMM does not directly output internal resistance, so we calculate it as:
# Internal resistance = (Battery open-circuit voltage - Terminal voltage) / Current
current = solution["Current [A]"].data
voltage = solution["Terminal voltage [V]"].data
ocv = solution["Battery open-circuit voltage [V]"].data  # Use "Battery open-circuit voltage [V]"
internal_resistance = (ocv - voltage) / current

# Plot the internal resistance growth over time
plt.figure(figsize=(10, 6))
plt.plot(solution.t, internal_resistance, label="Internal Resistance Growth", color="red")
plt.xlabel("Time [s]")
plt.ylabel("Internal Resistance [Ohm]")
plt.title("Internal Resistance Growth Using DFN Model")
plt.legend()
plt.grid(True)
plt.show()
