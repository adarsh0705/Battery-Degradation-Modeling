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
            "Charge at 1C until 4.2V",
            "Hold at 4.2V until C/50",
            "Discharge at 1C until 3V",
            "Rest for 1 hour",
        )
    ] * N
)

charge_experiment = pybamm.Experiment(
    [
        (
            "Charge at 1C until 4.2V",
            "Hold at 4.2V until C/50",
        )
    ]
)

rpt_experiment = pybamm.Experiment([("Discharge at C/3 until 3V",)])

# First simulation for CCCV experiment
sim = pybamm.Simulation(model, experiment=cccv_experiment, parameter_values=parameter_values)
cccv_sol = sim.solve()

# Second simulation for Charge experiment
sim = pybamm.Simulation(model, experiment=charge_experiment, parameter_values=parameter_values)
charge_sol = sim.solve(starting_solution=cccv_sol)

# Third simulation for RPT experiment
sim = pybamm.Simulation(model, experiment=rpt_experiment, parameter_values=parameter_values)
rpt_sol = sim.solve(starting_solution=charge_sol)

# Plot last RPT cycle
pybamm.dynamic_plot(rpt_sol.cycles[-1], ["Current [A]", "Voltage [V]"])
pybamm.plot_summary_variables(rpt_sol)

# Run multiple sets of experiments (M sets)
cccv_sols = []
charge_sols = []
rpt_sols = []
M = 5

for i in range(M):
    if i != 0:  # Skip the first set of ageing cycles because it's already been done
        sim = pybamm.Simulation(model, experiment=cccv_experiment, parameter_values=parameter_values)
        cccv_sol = sim.solve(starting_solution=rpt_sol)
        sim = pybamm.Simulation(model, experiment=charge_experiment, parameter_values=parameter_values)
        charge_sol = sim.solve(starting_solution=cccv_sol)
        sim = pybamm.Simulation(model, experiment=rpt_experiment, parameter_values=parameter_values)
        rpt_sol = sim.solve(starting_solution=charge_sol)
    
    cccv_sols.append(cccv_sol)
    charge_sols.append(charge_sol)
    rpt_sols.append(rpt_sol)



# Collect capacities for CCCV and RPT cycles
cccv_cycles = []
cccv_capacities = []
rpt_cycles = []
rpt_capacities = []

for i in range(M):
    for j in range(N):
        cccv_cycles.append(i * (N + 2) + j + 1)
        start_capacity = rpt_sols[i].cycles[j].steps[2]["Discharge capacity [A.h]"].entries[0]
        end_capacity = rpt_sols[i].cycles[j].steps[2]["Discharge capacity [A.h]"].entries[-1]
        cccv_capacities.append(end_capacity - start_capacity)
    
   # rpt_cycles.append((i + 1) * (N + 2))
    start_capacity = rpt_sols[i].cycles[-1]["Discharge capacity [A.h]"].entries[0]
    end_capacity = rpt_sols[i].cycles[-1]["Discharge capacity [A.h]"].entries[-1]
    rpt_capacities.append(end_capacity - start_capacity)




# Plot the capacity fade over cycles
plt.scatter(cccv_cycles, cccv_capacities)
plt.legend()
plt.show()



