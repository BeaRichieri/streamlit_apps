The **hydrotope storage** $E_{i,t}$ changes according to the hydrotope-specific source and sink term $S_{i,t}$ and three outflow components.

$S_{i,t}$ (mm/$\Delta t$) is the hydrotope-specific **net source and sink term**, accounting for inputs and losses such as precipitation, snowmelt, evapotranspiration and interception.

The fluxes in the water balance are:

- $Q_{\mathrm{is},i,t}$ (m³/$\Delta t$): **slow infiltration** / groundwater recharge from hydrotope $i$ toward the **matrix** compartment;
- $Q_{\mathrm{hyd},i,t}$ (m³/$\Delta t$): **fast flow** from hydrotope $i$ toward the **conduit** compartment;
- $Q_{\mathrm{sec},i,t}$ (m³/$\Delta t$): **secondary spring discharge**, which leaves the modeled catchment directly when the secondary-flow threshold is exceeded.

The index $i$ identifies the hydrotope and $\Delta t$ is the simulation time step. The maximum operator prevents negative storage.

**Symbols in this equation**

| Symbol | Unit | Interpretation |
|---|---:|---|
| $E_{i,t}$ | mm | Water level (storage depth) in hydrotope $i$ at time step $t$. |
| $A_i$ | m² | Area represented by hydrotope $i$. It determines the spatial contribution of the hydrotope to the catchment response. |
| $\Delta t$ | time | Simulation time step. |
