import pybamm
import matplotlib.pyplot as plt

# Set logging level
pybamm.set_logging_level("NOTICE")

# Set up the second model and parameters (with aging mechanisms)
model = pybamm.lithium_ion.DFN(options={
    "SEI": "solvent-diffusion limited",
    "SEI porosity change": "true",
    "particle mechanics": "swelling and cracking",
    "SEI on cracks": "true",
})

param = pybamm.ParameterValues("OKane2022")
var_pts = {"x_n": 10, "x_s": 10, "x_p": 10, "r_n": 16, "r_p": 16}
param["Ambient temperature [K]"] = 298.15  # Fixed at 25°C

# Define the experimental protocol
experiment = pybamm.Experiment(
    [
        (
            "Discharge at 0.8A for 0.4 seconds",
            "Charge at 1A for 0.3 seconds",
            "Charge at 0.8A for 0.3 seconds",
            "Discharge at 1A for 0.2 seconds",
            "Charge at 1A for 0.4 seconds",
            "Discharge at 1A for 2.0 seconds",
            "Discharge at 1A for 0.4 seconds",
            "Charge at 0.7A for 6.3 seconds",
            "Discharge at 0.7A for 3.4 seconds",
            "Discharge at 0.7A for 5.7 seconds",
            "Charge at 1A for 0.4 seconds",
            "Discharge at 1A for 0.5 seconds",
            "Charge at 1A for 6.7 seconds",
            "Discharge at 1A for 0.2 seconds",
            "Discharge at 0.6A for 8.7 seconds",
            "Discharge at 0.6A for 0.4 seconds",
            "Charge at 0.6A for 7.0 seconds",
            "Charge at 0.6A for 0.3 seconds",
            "Discharge at 1A for 0.2 seconds",
            "Discharge at 1A for 0.1 seconds",
            "Rest for 1.1 seconds",
            "Discharge at 5A for 30 seconds",
            "Discharge at 10A for 15 seconds",
            "Rest for 10 seconds"
        )*100
    ],
    period="0.1 seconds",
    termination="1V"
)

# Create simulation object for the Model with the IDAKLUSolver
solver = pybamm.IDAKLUSolver(rtol=1e-6, atol=1e-8)  # Use a specific solver with set tolerances
simulation = pybamm.Simulation(model, experiment=experiment, parameter_values=param, var_pts=var_pts, solver=solver)
print("Starting simulation for Model ...")
solution = simulation.solve()
time = solution["Time [s]"].entries
voltage = solution["Terminal voltage [V]"].entries

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(time, voltage, label="Model  (with aging)", linestyle="--")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)")
plt.title("Voltage vs Time for Model  (with aging)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()