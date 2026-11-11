## Exercise 4 — Release from the lower compartments to the spring

### Goal
Understand how the conduit and matrix outlet parameters control the release of stored water to the modeled spring.

### Mechanism
The two possible spring-discharge components are

$$
Q_{\mathrm{CS}}=A\,k_{\mathrm{CS}}\,C^{a_{\mathrm{CS}}}
$$

and

$$
Q_{\mathrm{MS}}=A\,k_{\mathrm{MS}}\,M^{a_{\mathrm{MS}}}.
$$

For the Baget reference parameterization, `kMS = 0`, so $Q_{\mathrm{MS}}=0$ and simulated spring discharge is controlled almost entirely by $Q_{\mathrm{CS}}$.

### Experiment A — Conduit drainage coefficient
Start from the reference values.

1. Reference: `kCS = 7.74e-3`.
2. Reduce `kCS` to about `2e-3`.
3. Inspect `Conduit storage C`, `QCS`, and simulated spring discharge.
4. Reset and increase `kCS` to about `3e-2`.

### Question 1
For the same conduit storage, what does a larger `kCS` do to $Q_{\mathrm{CS}}$?

:::answer Answer to question 1
It increases $Q_{\mathrm{CS}}$ directly. The conduit therefore releases water more efficiently toward the spring. Because the storage is also evolving, a larger `kCS` generally causes the conduit to drain faster and changes the recession following recharge events.
:::endanswer

### Question 2
Why does the simulated spring discharge almost overlap $Q_{\mathrm{CS}}$ in the reference run?

:::answer Answer to question 2
Because `kMS = 0`, the direct matrix-to-spring flux is switched off. Therefore $Q_{\mathrm{sim}}=Q_{\mathrm{CS}}+Q_{\mathrm{MS}}$ reduces approximately to $Q_{\mathrm{sim}}=Q_{\mathrm{CS}}$.
:::endanswer

### Experiment B — Activate direct matrix discharge
Reset first.

1. Increase `kMS` from `0` to about `0.02`.
2. Display `QMS - Matrix to spring`, `QCS - Conduit to spring`, and simulated spring discharge.
3. Inspect matrix storage and the recession periods between rainfall events.

### Question 3
What new behaviour appears when `kMS` is greater than zero?

:::answer Answer to question 3
A direct matrix-to-spring pathway is activated. Part of the water stored in the matrix can now contribute directly to spring discharge instead of reaching the spring only indirectly through $Q_{\mathrm{MC}}$ and the conduit. This can increase the slower, more sustained component of the hydrograph and alter recession behaviour.
:::endanswer

### Optional challenge — Change `aCS`
Reset and reduce `aCS` from `3.85` to about `2.0`, keeping `kCS` fixed.

How does this change the contrast between low- and high-storage conduit conditions?

:::answer Optional challenge answer
The reference exponent is strongly nonlinear. Lowering $a_{\mathrm{CS}}$ reduces the strong amplification of high conduit storage, so the outlet relation becomes less nonlinear and the contrast between low-flow and high-flow release is reduced.
:::endanswer

### Take-home message
Outlet parameters control not only the magnitude of spring discharge but also how quickly each storage compartment is emptied. Activating or deactivating a pathway can effectively change the conceptual model structure.

**Before continuing:** reset to the Baget reference values.
