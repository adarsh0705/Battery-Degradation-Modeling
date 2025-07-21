import pybamm
import matplotlib.pyplot as plt

# Set logging level
pybamm.set_logging_level("NOTICE")

# Set up the second model and parameters (with aging mechanisms)
model2 = pybamm.lithium_ion.DFN(options={
    "SEI": "solvent-diffusion limited",
    "SEI porosity change": "true",
    "particle mechanics": "swelling and cracking",
    "SEI on cracks": "true",
})

param2 = pybamm.ParameterValues("Chen2020")
var_pts2 = {"x_n": 10, "x_s": 10, "x_p": 10, "r_n": 16, "r_p": 16}
param2["Ambient temperature [K]"] = 298.15  # Fixed at 25°C

# Define the experimental protocol for 100 cycles
experiment = pybamm.Experiment(
    [
        (
             # Step 1: Hold at 4.2V until C/100 (current falls below 50 mA)
        "Hold at 4.2 V until C/100",
        
        # Step 3: Discharge at 0.5A until 2.5V
        "Discharge at 0.5 A until 2.5 V",
        
        # Step 4: Charge at 1.5A until 4.2V
        "Charge at 1.5 A until 4.2 V",
        
        # Step 5: Hold at 4.2V until C/100 (current falls below 50 mA)
        "Hold at 4.2 V until C/100",

         # Step 2: Rest for 4 hours
        "Rest for 4 hours",

        )
    ] * 100,  # Repeat this protocol for 100 cycles
   
)

# Create simulation object for Model 2
simulation2 = pybamm.Simulation(model2, experiment=experiment, parameter_values=param2, var_pts=var_pts2)
print("Starting simulation for Model 2 (100 cycles)...")
solution2 = simulation2.solve()
time2 = solution2["Time [s]"].entries
voltage2 = solution2["Terminal voltage [V]"].entries

# Plot results
plt.figure(figsize=(10, 6))
plt.plot(time2, voltage2, label="Model 2 (100 cycles with aging)", linestyle="--")
plt.xlabel("Time (s)")
plt.ylabel("Voltage (V)" )
plt.title("Voltage vs Time for Model 2 (100 cycles with aging)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.show()