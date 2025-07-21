import pybamm
import matplotlib.pyplot as plt

# Define the initial capacity
initial_capacity = 5  # 5 Ah

# Define the number of cycles
num_cycles = 1000

# Define a simple linear capacity fade model
capacity_fade_rate = 0.001  # 0.1% capacity fade per cycle

# Create an array to store the capacity at each cycle
capacity = [initial_capacity]

# Simulate the capacity fade over the number of cycles
for cycle in range(1, num_cycles + 1):
    capacity.append(capacity[-1] * (1 - capacity_fade_rate))

# Plot the capacity fade graph
plt.plot(range(num_cycles + 1), capacity, label="Capacity Fade")
plt.xlabel("Cycle Number")
plt.ylabel("Capacity (Ah)")
plt.title("Capacity Fade Over Cycles")
plt.grid(True)
plt.legend()
plt.show()