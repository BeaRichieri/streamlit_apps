#### Exercise 2 - Generation of fast flow

### Mechanism

The fast-flow response is described by

$$
Q_{\mathrm{hyd},i,t}
=
\varepsilon_{i,t}
\left(
\frac{\max(0,E_{i,t}-E_{\min,i})}
{E_{\max,i}-E_{\min,i}}
\right)^{\alpha_i}
\frac{k_{\mathrm{hyd},i}}{l_{\mathrm{hyd},i}}
A_i
$$

The fast-flow parameters have **different physical roles**. Investigate them separately rather than changing them together.

Use **one hydrotope at a time** and reset to the reference values between the three experiments below.

### A. Activation and deactivation — `Emin` and `Emax`

#### Predict

What should happen to the timing of fast flow if the activation/deactivation thresholds are shifted?

#### Experiment

1. Start from the **Reference** simulation.
2. Change `Emax` for one hydrotope while keeping the other parameters fixed.
3. Compare a lower and a higher `Emax`.
4. Repeat for `Emin`.

#### Inspect

Focus on:

- epikarst storage $E$;
- `Qhyd` of the selected hydrotope;
- conduit storage;
- `QCS`;
- simulated spring peak.

**Guiding question:** Which parameter mainly changes **when** fast flow becomes active and inactive?

---

### B. Shape of the fast response — `alpha`

#### Predict

`alpha` is an exponent. Do you expect it to mainly shift the threshold, or to change how strongly `Qhyd` grows once the pathway is active?

#### Experiment

1. Reset to the reference.
2. Change only `alpha` for the selected hydrotope.
3. Compare a lower and a higher value.

#### Inspect

Compare the shape of `Qhyd` during events and how that shape propagates into conduit storage, `QCS`, and the spring peak.

**Guiding question:** Does `alpha` primarily affect activation timing or the **nonlinearity of the active fast-flow response**?

---

### C. Magnitude of fast flow — `khyd`

#### Predict

Because `khyd` multiplies the active fast-flow term, what should happen to `Qhyd` when `khyd` increases?

#### Experiment

1. Reset to the reference.
2. Change only `khyd`.
3. Use the logarithmic slider to compare values separated enough to make the effect visible.

#### Inspect

Follow:

**`khyd` → `Qhyd` → conduit storage → `QCS` → spring discharge**

**Guiding question:** How is changing the **magnitude** of fast transfer different from changing its thresholds or nonlinearity?

### Reset

Return to the **Baget reference values** before starting Exercise 3.
