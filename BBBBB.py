import pybamm
import numpy as np
import os

model = pybamm.BaseModel()
# dimensional parameters
k = pybamm.Parameter("Reaction rate constant [m.s-1]")
L_0 = pybamm.Parameter("Initial thickness [m]")
V_hat = pybamm.Parameter("Partial molar volume [m3.mol-1]")
c_inf = pybamm.Parameter("Bulk electrolyte solvent concentration [mol.m-3]")


def D(cc):
    return pybamm.FunctionParameter(
        "Diffusivity [m2.s-1]", {"Solvent concentration [mol.m-3]": cc}
    )
xi = pybamm.SpatialVariable("xi", domain="SEI layer", coord_sys="cartesian")
c = pybamm.Variable("Solvent concentration [mol.m-3]", domain="SEI layer")
L = pybamm.Variable("SEI thickness [m]")

# SEI reaction flux
R = k * pybamm.BoundaryValue(c, "left")

# solvent concentration equation
N = -1 / L * D(c) * pybamm.grad(c)
dcdt = (V_hat * R) / L * pybamm.inner(xi, pybamm.grad(c)) - 1 / L * pybamm.div(N)

# SEI thickness equation
dLdt = V_hat * R

model.rhs = {c: dcdt, L: dLdt}

D_left = pybamm.BoundaryValue(
    D(c), "left"
)  # pybamm requires BoundaryValue(D(c)) and not D(BoundaryValue(c))
grad_c_left = R * L / D_left


c_right = c_inf

model.boundary_conditions = {
    c: {"left": (grad_c_left, "Neumann"), "right": (c_right, "Dirichlet")}
}

c_init = c_inf
L_init = L_0

model.initial_conditions = {c: c_init, L: L_init}


model.variables = {
    "SEI thickness [m]": L,
    "SEI growth rate [m]": dLdt,
    "Solvent concentration [mol.m-3]": c,
}


# define geometry
geometry = pybamm.Geometry(
    {"SEI layer": {xi: {"min": pybamm.Scalar(0), "max": pybamm.Scalar(1)}}}
)


def Diffusivity(cc):
    return cc * 10 ** (-12)


# parameter values (not physically based, for example only!)
param = pybamm.ParameterValues(
    {
        "Reaction rate constant [m.s-1]": 1e-6,
        "Initial thickness [m]": 1e-6,
        "Partial molar volume [m3.mol-1]": 10,
        "Bulk electrolyte solvent concentration [mol.m-3]": 1,
        "Diffusivity [m2.s-1]": Diffusivity,
    }
)

# process model and geometry
param.process_model(model)
param.process_geometry(geometry)

# mesh and discretise
submesh_types = {"SEI layer": pybamm.Uniform1DSubMesh}
var_pts = {xi: 100}
mesh = pybamm.Mesh(geometry, submesh_types, var_pts)

spatial_methods = {"SEI layer": pybamm.FiniteVolume()}
disc = pybamm.Discretisation(mesh, spatial_methods)
disc.process_model(model)

<pybamm.models.base_model.BaseModel at 0x7f3a8005b490>

# solve
solver = pybamm.ScipySolver()
t = [0, 100]  # solve for 100s
solution = solver.solve(model, t)

# post-process output variables
L_out = solution["SEI thickness [m]"]
c_out = solution["Solvent concentration [mol.m-3]"]

import matplotlib.pyplot as plt

# plot SEI thickness in microns as a function of t in microseconds
# and concentration in mol/m3 as a function of x in microns
L_0_eval = param.evaluate(L_0)
xi = np.linspace(0, 1, 100)  # dimensionless space


def plot(t):
    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
    ax1.plot(solution.t, L_out(solution.t) * 1e6)
    ax1.plot(t, L_out(t) * 1e6, "r.")
    ax1.set_ylabel(r"SEI thickness [$\mu$m]")
    ax1.set_xlabel(r"t [s]")

    ax2.plot(xi * L_out(t) * 1e6, c_out(t, xi))
    ax2.set_ylim(0, 1.1)
    ax2.set_xlim(0, L_out(solution.t[-1]) * 1e6)
    ax2.set_ylabel("Solvent concentration [mol.m-3]")
    ax2.set_xlabel(r"x [$\mu$m]")

    plt.tight_layout()
    plt.show()


