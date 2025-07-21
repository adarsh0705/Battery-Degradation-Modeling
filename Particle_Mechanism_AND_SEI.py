import pybamm
import matplotlib.pyplot as plt
model1 = pybamm.lithium_ion.DFN(
    {"SEI": "solvent-diffusion limited", "particle mechanics": "swelling only"}
)
model2 = pybamm.lithium_ion.DFN(
    {
        "particle mechanics": "swelling and cracking",
        "SEI": "solvent-diffusion limited",
        "SEI on cracks": "true",
        
    }
)
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
sim1 = pybamm.Simulation(
    model1, parameter_values=param, experiment=exp, var_pts=var_pts
)

sol1 = sim1.solve(calc_esoh=False)
sim2 = pybamm.Simulation(
    model2, parameter_values=param, experiment=exp, var_pts=var_pts
)
sol2 = sim2.solve(calc_esoh=False)
t1 = sol1["Time [s]"].entries
V1 = sol1["Voltage [V]"].entries
SEI1 = sol1["Loss of lithium to negative SEI [mol]"].entries
lithium_neg1 = sol1["Total lithium in negative electrode [mol]"].entries
lithium_pos1 = sol1["Total lithium in positive electrode [mol]"].entries
t2 = sol2["Time [s]"].entries
V2 = sol2["Voltage [V]"].entries
SEI2 = (
    sol2["Loss of lithium to negative SEI [mol]"].entries
    + sol2["Loss of lithium to negative SEI on cracks [mol]"].entries
)
lithium_neg2 = sol2["Total lithium in negative electrode [mol]"].entries
lithium_pos2 = sol2["Total lithium in positive electrode [mol]"].entries
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 4))
ax1.plot(t1, V1, label="without cracking")
ax1.plot(t2, V2, label="with cracking", linestyle="dashed")
ax1.set_xlabel("Time [s]")
ax1.set_ylabel("Voltage [V]")
ax1.legend()
ax2.plot(t1, SEI1, label="without cracking")
ax2.plot(t2, SEI2, label="with cracking", linestyle="dashed")
ax2.set_xlabel("Time [s]")
ax2.set_ylabel("Loss of lithium to SEI [mol]")
ax2.legend()
plt.show()
fig, ax = plt.subplots()
ax.plot(t2, lithium_neg2 + lithium_pos2)
ax.plot(t2, lithium_neg2[0] + lithium_pos2[0] - SEI2, linestyle="dashed")
ax.set_xlabel("Time [s]")
ax.set_ylabel("Total lithium in electrodes [mol]")
plt.show()
