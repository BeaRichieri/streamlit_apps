#### Exercise 5 - Conduit loss threshold

### Mechanism

Conduit loss is activated only when conduit storage exceeds the threshold $C_{\mathrm{loss}}$:

$$
Q_{\mathrm{Closs},t}
=
\begin{cases}
\left(C_t-C_{\mathrm{loss}}\right)
\dfrac{R_a}{\Delta t},
& C_t>C_{\mathrm{loss}},\\[4pt]
0,
& C_t\leq C_{\mathrm{loss}}.
\end{cases}
$$

The **Internal fluxes** graph includes `QCloss - Conduit loss`. It is hidden by default; click its legend entry to display it.

### 1. Predict

Before changing the threshold:

- What should happen to the frequency of conduit loss if `C_loss` is lowered?
- If more water leaves through `QCloss`, what should happen to the water available for `QCS`?
- Which part of the spring hydrograph do you expect to be most affected?

### 2. Experiment

1. Start from the **Reference** simulation.
2. Change only `C_loss`.
3. Compare a clearly lower and a clearly higher threshold using the logarithmic slider.

### 3. Inspect the threshold response

In **Internal fluxes**, display:

- `QCloss - Conduit loss`;
- `QCS - Conduit to spring`;
- simulated spring discharge.

In **Storages**, inspect conduit storage.

### 4. Interpret

Follow the causal chain:

**`C_loss` → activation of `QCloss` → conduit storage → `QCS` → spring discharge**

**Guiding question:** How does removing water through the conduit-loss pathway change the fraction of conduit water that remains available to discharge at the modeled spring?

### Finish

Reset to the **Baget reference values**. At this point you have investigated the main mechanisms one at a time. The next tutorial section will deliberately combine parameters to explore parameter interactions and equifinality.
