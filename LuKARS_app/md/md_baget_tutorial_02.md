## Exercise 2 — Fast hydrotope flow to the conduit

### Goal
Understand how $E_{\min}$, $E_{\max}$, $k_{\mathrm{hyd}}$, and $\alpha$ control the **activation, duration, magnitude, and shape** of rapid recharge from a hydrotope to the conduit.

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

Fast flow is hysteretic:

- it switches **ON** when $E_i \ge E_{\max,i}$;
- it switches **OFF** when $E_i \le E_{\min,i}$;
- between the two thresholds, the previous ON/OFF state is retained.

Define the normalized storage term

$$
r_i=
\frac{E_i-E_{\min,i}}
{E_{\max,i}-E_{\min,i}}.
$$

The thresholds therefore do more than switch the pathway on and off: they also change $r_i$, and hence the magnitude of $Q_{\mathrm{hyd},i}$ while the pathway is active.

---

### Experiment A — Change $E_{\max}$

Start from the reference simulation and work with **Hydrotope 1**.

1. Reference: `Emax = 142 mm`.
2. Lower `Emax` to about `60 mm`.
3. Inspect `Epikarst storage E1`, `Qhyd - Hydrotope 1`, `Conduit storage C`, `QCS`, and simulated spring discharge.
4. Reset and increase `Emax` to about `180 mm`.

### Question 1
Why can changing $E_{\max}$ affect both **when fast flow starts** and **how large it becomes**?

:::answer Answer to question 1
$E_{\max}$ is the activation threshold, so lowering it makes fast-flow activation easier and generally earlier or more frequent.

But $E_{\max}$ also appears in the denominator of

$$
r=\frac{E-E_{\min}}{E_{\max}-E_{\min}}.
$$

For the same $E$ and $E_{\min}$, lowering $E_{\max}$ makes the denominator smaller and generally increases $r$, so $Q_{\mathrm{hyd}}$ can also become larger once the pathway is active.

Changing $Q_{\mathrm{hyd}}$ then changes how quickly the epikarst drains, so the storage trajectory itself also changes.
:::endanswer

### Question 2
Which part of the spring hydrograph is most likely to react to this change?

:::answer Answer to question 2
The strongest effect is usually around recharge events and spring-discharge peaks, because $Q_{\mathrm{hyd}}$ feeds the rapidly responding conduit compartment directly.
:::endanswer

---

### Experiment B — Change $E_{\min}$

Reset first.

1. Reference: `Emin = 10.2 mm` for Hydrotope 1.
2. Increase `Emin` substantially, for example to `60–100 mm`, while keeping `Emin < Emax`.
3. Compare `Epikarst storage E1` and `Qhyd - Hydrotope 1`.
4. Reset and try a lower $E_{\min}$ again.

### Question 3
Does increasing $E_{\min}$ simply make fast flow switch off earlier?

:::answer Answer to question 3
Increasing $E_{\min}$ has two coupled effects. It raises the threshold at which an active fast-flow pathway can switch off, but it also changes the nonlinear fast-flow equation.

Because $Q_{\mathrm{hyd}}$ controls how quickly the epikarst drains, changing $E_{\min}$ also changes the simulated storage $E$. The resulting change in $Q_{\mathrm{hyd}}$ therefore cannot be predicted from $E_{\min}$ alone; the storage response must also be considered.

In the Baget experiment, increasing $E_{\min}$ raises the simulated epikarst storage and results in a larger fast-flow response. This is why simply increasing $E_{\min}$ does not necessarily make the switch-off easier to observe.
:::endanswer

### Take a moment
This is why $E_{\min}$ and $E_{\max}$ should not be interpreted as simple independent ON/OFF switches. They affect both the **state of the pathway** and the **strength of the flux**.

---

### Experiment C — Change the magnitude coefficient

Reset first.

1. Reference: `khyd ≈ 2730 m2/h` for Hydrotope 1.
2. Increase it to about `6000 m2/h`.
3. Then try a smaller value around `500 m2/h`.
4. Keep all other parameters fixed.

### Question 4
How is changing $k_{\mathrm{hyd}}$ different from changing the thresholds?

:::answer Answer to question 4
$k_{\mathrm{hyd}}$ mainly scales the magnitude of fast flow once the pathway is active.

By contrast, $E_{\min}$ and $E_{\max}$ also control the hysteretic activation/deactivation state and modify the normalized storage term. The thresholds therefore influence both **timing** and **magnitude**, while $k_{\mathrm{hyd}}$ acts mainly as a multiplicative scaling parameter.
:::endanswer

---

### Experiment D — Change the nonlinearity $\alpha$

Reset first.

1. Reference: `alpha = 1.98`.
2. Reduce it to about `1.0`.
3. Increase it to about `3.0`.
4. Compare the response during moderate-storage periods and during the largest recharge events.

Remember:

$$
Q_{\mathrm{hyd}}\propto r^\alpha,
\qquad
r=
\frac{E-E_{\min}}
{E_{\max}-E_{\min}}.
$$

### Question 5
Does increasing $\alpha$ always increase fast flow?

:::answer Answer to question 5
No. The effect depends on the value of the normalized storage term $r$.

- If $0<r<1$, increasing $\alpha$ makes $r^\alpha$ **smaller**, so fast flow decreases.
- If $r=1$, changing $\alpha$ has no effect on this term.
- If $r>1$, increasing $\alpha$ makes $r^\alpha$ **larger**, so fast flow increases.

Therefore a larger $\alpha$ can suppress fast flow at intermediate storage while amplifying it during very high-storage conditions. $\alpha$ changes the **shape and nonlinearity** of the fast-flow response, not simply its overall magnitude.
:::endanswer

### Question 6
Why can the effect of $\alpha$ look different at different times in the same simulation?

:::answer Answer to question 6
Because $r$ changes with epikarst storage. During one period the storage may give $0<r<1$, while during a strong recharge event it may give $r>1$. The same increase in $\alpha$ can therefore reduce $Q_{\mathrm{hyd}}$ at one time and increase it at another.
:::endanswer

---

### Take-home message
The fast pathway contains several interacting controls:

- $E_{\max}$ controls activation **and** changes the normalized storage term;
- $E_{\min}$ controls deactivation **and** changes the normalized storage term;
- $k_{\mathrm{hyd}}$ mainly scales the amount of fast flow;
- $\alpha$ controls the nonlinear shape, and its effect depends on whether $r$ is below or above 1.

**Before continuing:** reset to the Baget reference values.
