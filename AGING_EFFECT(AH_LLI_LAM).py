import pybamm
import matplotlib.pyplot as plt

# Define the model
model = pybamm.lithium_ion.DFN({"SEI": "ec reaction limited"})

# Set parameter values and update SEI kinetic rate constant
parameter_values = pybamm.ParameterValues("Chen2020")
parameter_values.update({"SEI kinetic rate constant [m.s-1]": 1e-14})

# Set N (number of repetitions in CCCV experiment)
N = 10

# Define experiments
cccv_experiment = pybamm.Experiment(
    [
        (
            "Discharge at 1C until 2.5V",
            "Charge at 0.3C until 4.2V (3 minute period)",
            "Hold at 4.2V until C/100 (3 minute period)"
        )
    ]
    * N,
)
charge_experiment = pybamm.Experiment(
    [
        (
            "Charge at 1C until 4.2V",
            "Hold at 4.2V until C/100",
        )
    ]
)

# First simulation for CCCV experiment
sim = pybamm.Simulation(model, experiment=cccv_experiment, parameter_values=parameter_values)
cccv_sol = sim.solve()

# Second simulation for Charge experiment
sim = pybamm.Simulation(model, experiment=charge_experiment, parameter_values=parameter_values)
charge_sol = sim.solve(starting_solution=cccv_sol)

# Simulate repeated aging cycles (CCCV and Charge) 
cccv_sols = []
charge_sols = []
M = 5  # Number of aging cycles
for i in range(M):
    if i != 0:  # skip the first set of ageing cycles because it's already been done
        sim = pybamm.Simulation(
            model, experiment=cccv_experiment, parameter_values=parameter_values
        )
        cccv_sol = sim.solve(starting_solution=charge_sol)
        sim = pybamm.Simulation(
            model, experiment=charge_experiment, parameter_values=parameter_values
        )
        charge_sol = sim.solve(starting_solution=cccv_sol)
    cccv_sols.append(cccv_sol)
    charge_sols.append(charge_sol)

# Collect capacities for CCCV cycles 
cccv_cycles = []
cccv_capacities = []

for i in range(M):
    for j in range(N):
        cccv_cycles.append(i * N + j + 1)
        start_capacity = cccv_sols[i].cycles[j].steps[2]["Discharge capacity [A.h]"].entries[0]
        end_capacity = cccv_sols[i].cycles[j].steps[2]["Discharge capacity [A.h]"].entries[-1]
        cccv_capacities.append(end_capacity - start_capacity)

# Plot summary variables for the last CCCV solution
pybamm.plot_summary_variables(cccv_sol)

# Plot the capacity fade over cycles
plt.plot(cccv_cycles, cccv_capacities, label="Capacity fade (CCCV)")
plt.xlabel("Cycle number")
plt.ylabel("Discharge capacity [A.h]")
plt.legend()
plt.show()


