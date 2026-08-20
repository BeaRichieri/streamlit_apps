#### Exercise 3 - Matrix-conduit coupling

### Mechanism

Matrix-conduit exchange is represented by

$$
Q_{\mathrm{MC},t}
=
R_a
k_{\mathrm{MC}}
\operatorname{sgn}(M_t-C_t)
|M_t-C_t|^{a_{\mathrm{MC}}}
$$

The exchange depends on both the **difference between matrix and conduit states** and the parameters `kMC` and `aMC`. The sign of `QMC` is important: the exchange can occur in either direction.

### 1. Predict

Before changing a parameter:

- When $M>C$, which direction should the exchange have?
- When $C>M$, which direction should it have?
- Which parameter do you expect to act mainly as an exchange-strength coefficient?
- Which parameter controls the nonlinearity with respect to $M-C$?

### 2. Experiment A — `kMC`

1. Start from the **Reference** simulation.
2. Change only `kMC`.
3. Compare a lower and a higher value using the logarithmic slider.

### 3. Inspect

In **Internal fluxes**, isolate `QMC` and identify periods with positive and negative values.

Then compare:

- matrix storage;
- conduit storage;
- `QCS`;
- simulated spring discharge.

### 4. Experiment B — `aMC`

1. Reset to the reference.
2. Change only `aMC`.
3. Again inspect `QMC` before looking at spring discharge.

### Interpret

**Guiding questions:**

- How does stronger/weaker matrix-conduit coupling redistribute water between the two lower compartments?
- How does changing `aMC` modify the response when the matrix-conduit state difference becomes large?
- Can a visible change in `QMC` produce only a modest change at the spring?

Explain the response through:

**`kMC` / `aMC` → `QMC` → matrix & conduit storage → `QCS` → spring discharge**

### Reset

Return to the **Baget reference values** before starting Exercise 4.
