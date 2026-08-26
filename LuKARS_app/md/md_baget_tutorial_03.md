## Exercise 3 — Matrix–conduit exchange

### Goal
Understand that $Q_{\mathrm{MC}}$ is a bidirectional internal flux and that changing internal exchange can alter storages even when the spring hydrograph changes only modestly.

### Mechanism
The exchange is controlled by the difference between matrix and conduit storage levels:

$$
Q_{\mathrm{MC}}
=
A\,k_{\mathrm{MC}}\,
\operatorname{sgn}(M-C)
\lvert M-C\rvert^{a_{\mathrm{MC}}}
$$

The sign determines the direction of exchange.

### Experiment
Start from the reference values.

1. Reference: `kMC = 2.06e-2`.
2. Decrease `kMC` to about `2e-3`.
3. Inspect `QMC`, `Matrix storage M`, `Conduit storage C`, `QCS`, and simulated spring discharge.
4. Reset and increase `kMC` to about `8e-2`.
5. Compare the two experiments with the reference.

### Question 1
How can you determine the direction of $Q_{\mathrm{MC}}$ from the storages?

:::answer Answer to question 1
If $M>C$, the storage gradient drives water from the matrix toward the conduit. If $C>M$, the direction reverses and water can move from the conduit toward the matrix. This is why $Q_{\mathrm{MC}}$ can change sign during a simulation.
:::endanswer

### Question 2
What does a larger `kMC` do to the difference between $M$ and $C$?

:::answer Answer to question 2
A larger $k_{\mathrm{MC}}$ strengthens the exchange for the same storage difference. Matrix and conduit therefore communicate more rapidly, which tends to reduce persistent differences between their storage states.
:::endanswer

### Question 3
Can two simulations have fairly similar spring discharge but noticeably different $M$, $C$, and $Q_{\mathrm{MC}}$?

:::answer Answer to question 3
Yes. The observed spring hydrograph constrains the combined outlet response, but it does not uniquely determine every internal state and flux. Different internal dynamics may compensate and produce similar outlet discharge. This is one reason why internal model behaviour and equifinality matter during calibration.
:::endanswer

### Optional challenge — Change `aMC`
Reset `kMC`, then change only `aMC` from `2.90` to about `1.5`.

What changes: a simple scaling of exchange, or the way exchange depends on the size of the storage difference?

:::answer Optional challenge answer
$a_{\mathrm{MC}}$ changes the **nonlinearity** of the exchange. It therefore changes how strongly small and large storage differences are weighted, rather than simply multiplying all $Q_{\mathrm{MC}}$ values by the same factor.
:::endanswer

### Take-home message
$Q_{\mathrm{MC}}$ is an internal, reversible coupling between the two lower compartments. Looking only at spring discharge can hide substantial differences in this internal exchange.

**Before continuing:** reset to the Baget reference values.
