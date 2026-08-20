#### Exercise 1 - Slow recharge and pathway partitioning

### Mechanism

Slow infiltration from hydrotope $i$ to the matrix is controlled by

$$
Q_{\mathrm{is},i,t}
=
k_{\mathrm{is},i}
E_{i,t}
A_i
$$

For the same hydrotope storage, increasing `kis` directly increases the transfer toward the matrix. Because this water leaves the hydrotope storage, it can also modify how much water remains available for fast flow.

### 1. Predict

Before changing anything, predict what should happen when `kis` is increased for **Hydrotope 1**:

- Will `Qis` increase or decrease?
- What should happen to matrix storage?
- Could `Qhyd` also change, even though `khyd`, `Emin`, `Emax`, and `alpha` remain fixed?
- Do you expect the effect to be stronger on the spring peak or on the later recession?

### 2. Experiment

1. Start from the saved **Reference** simulation.
2. Keep all parameters except `kis` unchanged.
3. Change `kis` for Hydrotope 1 first to a clearly lower value and then to a clearly higher value within its logarithmic range.
4. After each change, allow the model and live plots to update.

### 3. Inspect the internal response first

In **Internal fluxes**, compare:

- `Qis - Hydrotope 1`;
- `Qhyd - Hydrotope 1`;
- `QMC`.

In **Storages**, compare:

- epikarst storage of Hydrotope 1;
- matrix storage;
- conduit storage.

### 4. Then inspect the spring response

In **Calibration / Discharge**, compare:

- event peak magnitude;
- timing of the response;
- post-event recession;
- discharge between events.

### Interpret

**Guiding question:** How does transferring more water toward the slow pathway redistribute water between the fast response and the longer-term response?

Try to explain the spring hydrograph through the sequence:

**`kis` → `Qis` → hydrotope/matrix storage → lower-compartment fluxes → spring discharge**

### Reset

Return to the **Baget reference values** before starting Exercise 2.
