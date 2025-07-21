import pybamm
import matplotlib.pyplot as plt

# Define the model including LLI and LAM (loss of active material)
model = pybamm.lithium_ion.DFN(
    {
        "SEI": "solvent-diffusion limited",
        "SEI porosity change": "true",
        "particle mechanics": ("swelling and cracking", "swelling only"),
        "SEI on cracks": "true",
        "loss of active material": "stress-driven",  # LAM incorporated
    }
)

# Set the parameters
param = pybamm.ParameterValues("OKane2022")

# Discretization points
var_pts = {
    "x_n": 30,
    "x_s": 30,
    "x_p": 30,
    "r_n": 30,
    "r_p": 30,
}

# Number of cycles
cycle_number = 10

# Define the experiment
exp = pybamm.Experiment(
    [
        "Hold at 4.2 V until C/100 (5 minute period)",
        "Rest for 4 hours (5 minute period)",
        "Discharge at 0.1C until 2.5 V (5 minute period)",
        "Charge at 0.3C until 4.2 V (5 minute period)",
        "Hold at 4.2 V until C/100 (5 minute period)",
    ]
    + [
        (
            "Discharge at 1C until 2.5 V (1 minute period)",
            "Charge at 0.3C until 4.2 V (5 minute period)",
            "Hold at 4.2 V until C/100 (5 minute period)",
        )
    ]
    * cycle_number
    + ["Discharge at 0.1C until 2.5 V (5 minute period)"]
)

# Solver
solver = pybamm.IDAKLUSolver()

# Simulation
sim = pybamm.Simulation(
    model, parameter_values=param, experiment=exp, solver=solver, var_pts=var_pts
)

# Solve
sol = sim.solve()

# Extract data
Qt = sol["Throughput capacity [A.h]"].entries
Q_SEI = sol["Loss of capacity to negative SEI [A.h]"].entries
Q_SEI_cr = sol["Loss of capacity to negative SEI on cracks [A.h]"].entries
Q_LLI = sol["Total lithium lost [mol]"].entries * 96485.3 / 3600  # Convert to A.h
Q_LAM_n = sol["Loss of active material in negative electrode [%]"].entries
Q_LAM_p = sol["Loss of active material in positive electrode [%]"].entries

# ------------------------------


# Graph 1: Capacity loss [A.h]
# ------------------------------
plt.figure(figsize=(8, 5))
plt.plot(Qt, Q_SEI, label="SEI", linestyle="solid", linewidth=3.5)
plt.plot(Qt, Q_SEI_cr, label="SEI on cracks", linestyle="solid", linewidth=3.5)
plt.plot(Qt, Q_LLI, label="LLI", linestyle="solid", linewidth=3.5)
plt.xlabel("Throughput capacity [A.h]", fontsize=20)
plt.ylabel("Capacity loss [A.h]", fontsize=20)
plt.legend()
plt.tight_layout()
plt.show()



# Graph 2: Capacity loss [%]
# ------------------------------
plt.figure(figsize=(8, 5))
plt.plot(Qt, Q_LAM_n, label="LAM - Negative Electrode", linestyle="solid", linewidth=3.5)
plt.plot(Qt, Q_LAM_p, label="LAM - Positive Electrode", linestyle="solid", alpha=0.7, linewidth=3.5)
plt.xlabel("Throughput capacity [A.h]", fontsize=20)
plt.ylabel("Capacity loss [%]", fontsize=20)
plt.legend()
plt.tight_layout()
plt.show()