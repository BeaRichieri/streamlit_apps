## Exercise 1 — Slow infiltration to the matrix

### Goal
Understand how the slow hydrotope pathway $Q_{\mathrm{is}}$ redistributes recharge from the epikarst toward the matrix and how this can indirectly affect the spring response.

### Mechanism
For each hydrotope,

$$
Q_{\mathrm{is},i}=A_i\,k_{\mathrm{is},i}\,E_i
$$

A larger $k_{\mathrm{is}}$ means that, for the same epikarst storage $E$, more water is transferred toward the matrix.

### Experiment
Start from **Reset Baget parameters**. Work only with **Hydrotope 1**.

1. Note the reference value: `kis ≈ 8.11e-5 1/h`.
2. Increase `kis` by roughly one order of magnitude, to about `8e-4 1/h`.
3. In **Internal fluxes**, display:
   - `Qis - Hydrotope 1`;
   - `Qhyd - Hydrotope 1`;
   - `QMC - Matrix-conduit exchange`;
   - simulated spring discharge.
4. In **Storages**, display `Epikarst storage E1`, `Matrix storage M`, and `Conduit storage C`.
5. Compare the modified simulation with the reference.
6. As a contrast, try a smaller value around `8e-6 1/h`.

### Question 1
When `kis` is increased, what happens first to $Q_{\mathrm{is}}$ and to epikarst storage $E_1$?

:::answer Answer to question 1
For a given $E_1$, increasing $k_{\mathrm{is}}$ directly increases $Q_{\mathrm{is}}$. Because water leaves the hydrotope faster through the slow pathway, $E_1$ tends to be lower than in the reference run.
:::endanswer

### Question 2
How can a stronger slow pathway influence the fast pathway $Q_{\mathrm{hyd}}$?

:::answer Answer to question 2
The two pathways compete for water stored in the same hydrotope. A stronger $Q_{\mathrm{is}}$ tends to reduce $E_1$. This can make it more difficult for the hydrotope to reach or remain above the thresholds controlling $Q_{\mathrm{hyd}}$. Therefore fast-flow events may become weaker or less frequent.
:::endanswer

### Question 3
Why can matrix storage increase even though the Baget reference model has no direct matrix-to-spring discharge?

:::answer Answer to question 3
In the Baget reference parameterization, $k_{\mathrm{MS}}=0$, so $Q_{\mathrm{MS}}=0$. Water entering the matrix can nevertheless influence the spring indirectly through matrix-conduit exchange $Q_{\mathrm{MC}}$, then leave the conduit through $Q_{\mathrm{CS}}$.
:::endanswer

### Take-home message
`kis` does more than scale one internal flux. By changing how quickly water leaves the hydrotope toward the matrix, it also changes epikarst storage and therefore the competition between slow and fast recharge pathways.

**Before continuing:** reset to the Baget reference values.
