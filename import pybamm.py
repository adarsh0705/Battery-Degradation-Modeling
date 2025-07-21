import pybamm
import numpy as np
import matplotlib.pyplot as plt

# Define the model
model = pybamm.lithium_ion.DFN({"SEI": "ec reaction limited"})

# Set parameter values and update SEI kinetic rate constant
parameter_values = pybamm.ParameterValues("Chen2020")
parameter_values.update({"SEI kinetic rate constant [m.s-1]": 1e-14})

# Set N (number of repetitions in CCCV experiment)
N = 100

# Define experiments
cccv_experiment = pybamm.Experiment(
    [
        (
            "Charge at 1C until 4.2V",
            "Hold at 4.2V until C/50",
            "Discharge at 1C until 3V",
            "Rest for 1 hour",
        )
    ] * N
)

# First simulation for CCCV experiment
sim = pybamm.Simulation(model, experiment=cccv_experiment, parameter_values=parameter_values)
cccv_sol = sim.solve()

# Plot last CCCV cycle
pybamm.dynamic_plot(cccv_sol.cycles[-1], ["Current [A]", "Voltage [V]"])
pybamm.plot_summary_variables(cccv_sol)

# Run multiple sets of experiments (M sets)
cccv_sols = []
M = 5

for i in range(M):
    if i != 0:  # Skip the first set of ageing cycles because it's already been done
        sim = pybamm.Simulation(model, experiment=cccv_experiment, parameter_values=parameter_values)
        cccv_sol = sim.solve(starting_solution=cccv_sol)
    
    cccv_sols.append(cccv_sol)

# Collect capacities for CCCV cycles
cccv_cycles = []
cccv_capacities = []

for i in range(M):
    for j in range(N):
        cccv_cycles.append(i * (N + 2) + j + 1)
        start_capacity = cccv_sols[i].cycles[j].steps[2]["Discharge capacity [A.h]"].entries[0]
        end_capacity = cccv_sols[i].cycles[j].steps[2]["Discharge capacity [A.h]"].entries[-1]
        cccv_capacities.append(end_capacity - start_capacity)

 








# Plot the capacity fade over cycles
plt.scatter(cccv_cycles, cccv_capacities)
plt.legend()
plt.show()

