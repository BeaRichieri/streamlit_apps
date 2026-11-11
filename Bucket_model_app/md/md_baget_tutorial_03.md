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
Reset `kMC`, then change only `aMC` from `2.90` to `1.0`.

Display **M - C** together with **QMC** and compare the new simulation with the reference.

### Question 4
Why can reducing $a_{\mathrm{MC}}$ have only a modest effect when $|M-C|$ is around 0.6–0.7, but a much stronger effect — even a reversal of $Q_{\mathrm{MC}}$ — when $M$ and $C$ are much closer?

:::answer Answer to question 4
The key point is that changing $a_{\mathrm{MC}}$ also changes the simulated difference $M-C$.

The exchange is proportional to

$$
Q_{\mathrm{MC}}
\propto
\operatorname{sgn}(M-C)
|M-C|^{a_{\mathrm{MC}}}.
$$

In the reference simulation, for example, you may have approximately

$$
|M-C| \approx 0.67,
\qquad
a_{\mathrm{MC}}\approx 3.
$$

The exchange-driving term is then

$$
0.67^3 \approx 0.30.
$$

When $a_{\mathrm{MC}}$ is reduced to 1, matrix and conduit become more strongly coupled when their storages are close. Their difference can therefore become much smaller, for example

$$
|M-C| \approx 0.30.
$$

But now

$$
0.30^1 = 0.30.
$$

So a **smaller $M-C$ can produce almost the same $Q_{\mathrm{MC}}$**. This is why the peaks of $Q_{\mathrm{MC}}$ can remain similar even though the black $M-C$ curve becomes much smaller.

The largest difference appears when $M$ and $C$ are already very close. With $a_{\mathrm{MC}}\approx3$, a small difference is strongly suppressed:

$$
0.2^3 = 0.008.
$$

With $a_{\mathrm{MC}}=1$, small differences remain important. The stronger coupling can also make $M$ and $C$ cross. When $M-C$ changes sign, $Q_{\mathrm{MC}}$ changes direction and can become negative, meaning **conduit → matrix**.

**Main idea:** do not interpret the effect of $a_{\mathrm{MC}}$ from the exponent alone. Changing the exponent also changes $M$ and $C$, so always compare the new **M - C** and **QMC** curves together.
:::endanswer

### Take-home message
$Q_{\mathrm{MC}}$ is an internal, reversible coupling between the two lower compartments. Looking only at spring discharge can hide substantial differences in this internal exchange.

**Before continuing:** reset to the Baget reference values.
