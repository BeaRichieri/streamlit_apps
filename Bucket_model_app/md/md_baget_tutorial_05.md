## Exercise 5 — Conduit loss threshold

### Goal
Understand the threshold-controlled loss pathway and distinguish water discharged at the modeled spring from water removed from the conduit through $Q_{\mathrm{Closs}}$.

### Mechanism
Conduit loss is activated only when conduit storage exceeds the threshold $C_{\mathrm{loss}}$:

$$
Q_{\mathrm{Closs}}
=
\begin{cases}
(C-C_{\mathrm{loss}})\dfrac{A}{\Delta t}, & C>C_{\mathrm{loss}},\\
0, & C\le C_{\mathrm{loss}}.
\end{cases}
$$

### Experiment
Start from the reference values.

1. Reference: `C_loss = 2`.
2. In **Internal fluxes**, display:
   - `QCloss - Conduit loss`;
   - `QCS - Conduit to spring`;
   - simulated spring discharge.
3. In **Storages**, display `Conduit storage C`.
4. Lower `C_loss` to about `1`.
5. Reset and then increase `C_loss` to about `10`.

### Question 1
What happens to the activation of $Q_{\mathrm{Closs}}$ when the threshold is lowered?

:::answer Answer to question 1
The conduit reaches the lower threshold more easily. Conduit loss therefore activates more frequently and/or for larger amounts of water.
:::endanswer

### Question 2
What happens to conduit storage when $C>C_{\mathrm{loss}}$?

:::answer Answer to question 2
The amount above the threshold is removed through $Q_{\mathrm{Closs}}$. The threshold therefore acts as an upper limit on conduit storage in this model formulation.
:::endanswer

### Question 3
Why can lowering `C_loss` reduce spring-discharge peaks?

:::answer Answer to question 3
More water is removed through the loss pathway before it can remain stored in the conduit and leave through $Q_{\mathrm{CS}}$. Lower conduit storage also reduces the nonlinear conduit-to-spring discharge. Therefore a smaller fraction of rapid recharge remains available for the modeled spring.
:::endanswer

### Question 4
What should happen if `C_loss` is increased so much that conduit storage never reaches it?

:::answer Answer to question 4
$Q_{\mathrm{Closs}}$ remains zero. The threshold pathway is effectively inactive during the simulated period, and conduit water can instead be stored, exchanged with the matrix, or released through $Q_{\mathrm{CS}}$.
:::endanswer

### Take-home message
$C_{\mathrm{loss}}$ is not a continuous drainage coefficient. It is a **threshold** that determines when an additional loss pathway becomes active.

### Final reflection
You have now changed one mechanism at a time. Compare the five exercises and ask yourself:

- Which parameters mostly change **pathway partitioning**?
- Which mostly change **timing or activation**?
- Which mostly change **drainage from storage**?
- Could different parameter changes compensate for one another and create similar spring hydrographs?

That final question connects this manual investigation directly to **sensitivity analysis, parameter uncertainty, and equifinality**.

**Finish by resetting to the Baget reference values.**
