import pybamm
import matplotlib.pyplot as plt

# Define Model 2 with aging only
model2 = pybamm.lithium_ion.DFN(
    {
        "particle mechanics": "swelling and cracking",
        "SEI": "solvent-diffusion limited",
        "SEI on cracks": "true",
    }
)

# Parameter values and experiment setup
param = pybamm.ParameterValues("OKane2022")
var_pts = {
    "x_n": 20,  # negative electrode
    "x_s": 20,  # separator
    "x_p": 20,  # positive electrode
    "r_n": 26,  # negative particle
    "r_p": 26,  # positive particle
}
exp = pybamm.Experiment(
    ["Hold at 4.2 V until C/100", "Rest for 1 hour", "Discharge at 1C until 2.5 V"]
)

# Simulation with Model 2 (aging effects included)
solver = pybamm.IDAKLUSolver()
sim2 = pybamm.Simulation(
    model2, parameter_values=param, experiment=exp, var_pts=var_pts, solver=solver
)
sol2 = sim2.solve(calc_esoh=False)

# Extract results
t2 = sol2["Time [s]"].entries
SEI2 = sol2["Loss of lithium to negative SEI [mol]"].entries
SEI_on_cracks = sol2["Loss of lithium to negative SEI on cracks [mol]"].entries

# Plot SEI formation and SEI on cracks
plt.figure(figsize=(10, 5))
plt.plot(t2, SEI2, label="SEI formation", linestyle="solid")
plt.plot(t2, SEI_on_cracks, label="SEI on cracks", linestyle="dashed")
plt.xlabel("Time [s]")
plt.ylabel("Loss of lithium [mol]")
plt.title("SEI Formation and SEI on Cracks")
plt.legend()
plt.show()
