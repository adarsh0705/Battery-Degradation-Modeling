import pybamm
import numpy as np
import matplotlib.pyplot as plt

# 1. Define model with degradation mechanisms
model = pybamm.lithium_ion.DFN({
    "thermal": "lumped",
    "SEI": "ec reaction limited",
    "lithium plating": "irreversible",
})

# 2. Modified parameters for less aggressive behavior
param = pybamm.ParameterValues("OKane2022")
param.update({
    "Lower voltage cut-off [V]": 3.0,  # Increased lower cut-off
    "Upper voltage cut-off [V]": 4.1,  # Reduced upper cut-off
    "Total heat transfer coefficient [W.m-2.K-1]": 5.0,  # Increased cooling
    "Cell cooling surface area [m2]": 0.01,  # Larger surface area
    "Ambient temperature [K]": 298.15,
})

# 3. Less aggressive cycling protocol
cycle = [
    (
        "Rest for 300 seconds",  # Longer rest
        "Discharge at 10C until 2.5 V",  # Reduced discharge rate
        "Rest for 300 seconds",
        "Charge at 3C until 4.1 V",  # Reduced charge rate
        "Hold at 4.1 V until C/20",  # Reduced hold current
        "Rest for 300 seconds"
    )
]
experiment = pybamm.Experiment(cycle * 1, temperature=298.15)  # Run one cycle at a time

# 4. Solver configuration
solver = pybamm.IDAKLUSolver(rtol=1e-6, atol=1e-8)

# 5. Initial simulation
sim = pybamm.Simulation(model, parameter_values=param, experiment=experiment, solver=solver)

# Store initial solution
try:
    solution = sim.solve(npts=500)
except pybamm.SolverError as e:
    print(f"Solver failed: {e}")
    exit()  # Stop if the initial simulation fails

# Store results
all_data = {
    "time": list(solution["Time [s]"].entries),
    "voltage": list(solution["Terminal voltage [V]"].entries),
    "current": list(solution["Current [A]"].entries),
    "temperature": list(solution["X-averaged cell temperature [K]"].entries),
    "dTdt": list(np.gradient(
        solution["X-averaged cell temperature [K]"].entries,
        solution["Time [s]"].entries)),
}

# 6. Continued cycling with enhanced termination checks
n_cycles = 1  # Start from cycle 1
thermal_runaway_detected = False
dTdt_threshold = 1.0
max_temp = 393.15
MAX_CYCLES = 5  # Run for up to 50 cycles

while not thermal_runaway_detected and n_cycles <= MAX_CYCLES:
    print(f"🔥 Running cycle {n_cycles}...")

    # Run one cycle at a time
    experiment = pybamm.Experiment(cycle * 1, temperature=298.15)

    try:
        sim_cont = pybamm.Simulation(
            model,
            parameter_values=param,
            experiment=experiment,
            solver=solver
        )

        solution = sim_cont.solve(npts=500)

    except Exception as e:
        print(f"⚠️ Solver failed at cycle {n_cycles}: {str(e)}")
        break

    # Process results
    time = solution["Time [s]"].entries
    voltage = solution["Terminal voltage [V]"].entries
    current = solution["Current [A]"].entries
    temperature = solution["X-averaged cell temperature [K]"].entries
    dT_dt = np.gradient(temperature, time)

    # Debug monitoring
    print(f"Cycle {n_cycles}: Max temp {np.max(temperature)-273.15:.1f}°C, Max dT/dt {np.max(dT_dt):.2f} K/s")

    # Append results with offset
    time_offset = all_data["time"][-1]
    all_data["time"].extend(time + time_offset)
    all_data["voltage"].extend(voltage)
    all_data["current"].extend(current)
    all_data["temperature"].extend(temperature)
    all_data["dTdt"].extend(dT_dt)

    # Check thermal runaway at the END of each cycle
    if np.max(dT_dt) > dTdt_threshold or np.max(temperature) > max_temp:
        print(f"⚠️ Thermal runaway detected in cycle {n_cycles}")
        thermal_runaway_detected = True
        break  # Stop the simulation

    n_cycles += 1  # Increment cycle number

# Force stop if max cycles reached
if n_cycles > MAX_CYCLES:
    print(f"🛑 Stopped after {MAX_CYCLES} cycles without thermal runaway")

# 7. Plotting results
time = np.array(all_data["time"])
voltage = np.array(all_data["voltage"])
current = np.array(all_data["current"])
temperature = np.array(all_data["temperature"])
dTdt = np.array(all_data["dTdt"])

# Voltage/Current/Temperature plot
fig, ax1 = plt.subplots(figsize=(12, 6))
ax1.plot(time/3600, voltage, label="Voltage [V]", color='blue')
ax1.plot(time/3600, current, label="Current [A]", color='green', alpha=0.7)
ax1.set_xlabel("Time (hours)")
ax1.set_ylabel("Voltage/Current")
ax1.legend(loc="upper left")

ax2 = ax1.twinx()
ax2.plot(time/3600, temperature-273.15, label="Temperature [°C]", color='red')
ax2.axhline(120, color='black', linestyle='--', label="120°C Limit")
ax2.set_ylabel("Temperature (°C)")
ax2.legend(loc="upper right")
plt.title("Aggressive Cycling Thermal Behavior")
plt.grid(True)
plt.tight_layout()

# Thermal runaway indicators
plt.figure(figsize=(12, 4))
plt.plot(time/3600, dTdt, label="dT/dt", color='orange')
plt.axhline(1.0, color='red', linestyle='--', label="1 K/s Threshold")
plt.fill_between(time/3600, dTdt, where=(dTdt>1), color='red', alpha=0.3)
plt.xlabel("Time (hours)")
plt.ylabel("Temperature Rise Rate (K/s)")
plt.title("Thermal Runaway Progression")
plt.legend()
plt.grid(True)
plt.tight_layout()

plt.show()

print(f"\n🔋 Total cycles completed: {n_cycles-1}")
print(f"⏱️ Failure time: {time[-1]/3600:.1f} hours")
print(f"🌡️ Max temperature reached: {np.max(temperature)-273.15:.1f}°C")
print(f"🚨 Max dT/dt: {np.max(dTdt):.1f} K/s")
