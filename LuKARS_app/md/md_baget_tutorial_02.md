## Exercise 2 — Fast hydrotope flow to the conduit

### Goal
Understand how the activation threshold and discharge coefficient control rapid recharge from a hydrotope to the conduit.

### Mechanism
When fast flow is active, LuKARS uses

$$
Q_{\mathrm{hyd},i}
=
A_i\,\frac{k_{\mathrm{hyd},i}}{l_{\mathrm{hyd},i}}
\left(
\frac{E_i-E_{\min,i}}
{E_{\max,i}-E_{\min,i}}
\right)^{\alpha_i}
$$

Fast flow starts when storage reaches $E_{\max}$ and, once active, remains active until storage falls below $E_{\min}$.

### Experiment A — Change the activation threshold
Start from the reference simulation and work with **Hydrotope 1**.

1. Reference: `Emax = 142 mm`.
2. Lower `Emax` to about `60 mm`.
3. Inspect `Epikarst storage E1`, `Qhyd - Hydrotope 1`, `Conduit storage C`, `QCS`, and simulated spring discharge.
4. Reset and then increase `Emax` to about `180 mm`.

### Question 1
What happens to fast-flow activation when $E_{\max}$ is lowered?

:::answer Answer to question 1
Fast flow can activate at a lower epikarst storage, so activation generally occurs earlier and/or more often. In addition, the denominator $E_{\max}-E_{\min}$ becomes smaller, which tends to increase the normalized storage term once fast flow is active.
:::endanswer

### Question 2
Which part of the spring hydrograph is most likely to react to this change?

:::answer Answer to question 2
The most visible effect is usually around recharge events and spring-discharge peaks, because $Q_{\mathrm{hyd}}$ feeds the rapidly responding conduit compartment directly.
:::endanswer

### Experiment B — Change the magnitude of fast flow
Reset first.

1. Reference: `khyd ≈ 2730 m2/h` for Hydrotope 1.
2. Increase it to about `6000 m2/h`.
3. Then try a smaller value around `500 m2/h`.
4. Keep all other parameters fixed.

### Question 3
How is changing `khyd` different from changing `Emax`?

:::answer Answer to question 3
$E_{\max}$ mainly controls **when** the fast pathway activates. $k_{\mathrm{hyd}}$ mainly scales **how much** rapid flow is produced once the pathway is active. Both can change spring peaks, but through different mechanisms.
:::endanswer

### Optional challenge — Nonlinearity
Reset and reduce `alpha` from `1.98` to about `1.0`.

For normalized storage ratios between 0 and 1, what happens to the fast-flow term?

:::answer Optional challenge answer
For $0<r<1$, reducing the exponent increases $r^{\alpha}$. Therefore a smaller $\alpha$ generally makes the fast-flow response stronger over that part of the storage range. This parameter controls the shape of the response rather than only a simple multiplicative scale.
:::endanswer

### Take-home message
The fast pathway has both **activation controls** and **magnitude/shape controls**. Different parameters can therefore alter a spring peak for different physical reasons.

**Before continuing:** reset to the Baget reference values.
