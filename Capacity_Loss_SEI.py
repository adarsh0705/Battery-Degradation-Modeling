import pybamm
import matplotlib.pyplot as plt
model = pybamm.lithium_ion.DFN(
    {
        "SEI": "solvent-diffusion limited",
        "SEI porosity change": "true",
        "particle mechanics": ("swelling and cracking", "swelling only"),
        "SEI on cracks": "true",
       
    }
)

param = pybamm.ParameterValues("OKane2022")
var_pts = {
    "x_n": 5,  # negative electrode
    "x_s": 5,  # separator
    "x_p": 5,  # positive electrode
    "r_n": 30,  # negative particle
    "r_p": 30,  # positive particle
}
cycle_number = 10
exp = pybamm.Experiment(
    [
        "Hold at 4.2 V until C/100 (5 minute period)",
        "Rest for 4 hours (5 minute period)",
        "Discharge at 0.1C until 2.5 V (5 minute period)",  # initial capacity check
        "Charge at 0.3C until 4.2 V (5 minute period)",
        "Hold at 4.2 V until C/100 (5 minute period)",
    ]
    + [
        (
            "Discharge at 1C until 2.5 V (1 minute period)",  # ageing cycles
            "Charge at 0.3C until 4.2 V (5 minute period)",
            "Hold at 4.2 V until C/100 (5 minute period)",
        )
    ]
    * cycle_number
    + ["Discharge at 0.1C until 2.5 V (5 minute period)"],  # final capacity check
)
solver = pybamm.IDAKLUSolver()
sim = pybamm.Simulation(
    model, parameter_values=param, experiment=exp, solver=solver, var_pts=var_pts
)
sol = sim.solve()
Qt = sol["Throughput capacity [A.h]"].entries
Q_SEI = sol["Loss of capacity to negative SEI [A.h]"].entries
Q_SEI_cr = sol["Loss of capacity to negative SEI on cracks [A.h]"].entries
plt.figure()
plt.plot(Qt, Q_SEI, label="SEI", linestyle="dashed")
plt.plot(Qt, Q_SEI_cr, label="SEI on cracks", linestyle="dashdot")
plt.xlabel("Throughput capacity [A.h]")
plt.ylabel("Capacity loss [A.h]")
plt.legend()
plt.show()