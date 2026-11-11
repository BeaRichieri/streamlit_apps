# Steady-state reservoir experiments

Use the experiments below to investigate the behaviour of the conceptual reservoir.

Modify the sliders in the **steady-state interactive plot** in the original app tab.  
For a clear comparison, change **only one parameter at a time** and observe how the result changes.

## Experiment 1 — Linear reservoir

In the steady-state plot, begin with approximately:

$$
a = 0.010
$$

$$
b = 1.0
$$

$$
P = 1.5\ \mathrm{mm\,day^{-1}}
$$

$$
ET = 0.3\ \mathrm{mm\,day^{-1}}
$$

Observe the shape of the storage–discharge curve and the position of the equilibrium point.

### Questions

- What is the shape of the discharge curve when **b = 1**?
- At which point does discharge equal the net input **P − ET**?
- What does this intersection represent physically?

<details>
<summary><strong>💡 Show suggested answers</strong></summary>

**What is the shape of the discharge curve when b = 1?**  
The relationship is linear. Discharge increases in direct proportion to storage, so the storage–discharge relationship is represented by a straight line.

**At which point does discharge equal the net input P − ET?**  
Discharge equals the net input at the intersection between the storage–discharge curve and the horizontal net-input line.

**What does this intersection represent physically?**  
It represents the steady-state equilibrium. At this point, the amount of water entering the reservoir equals the amount leaving it, so storage no longer changes.

</details>

---

## Experiment 2 — Increase the nonlinearity

Keep **a**, **P** and **ET** unchanged, but gradually increase **b**:

$$
b = 1.0 \rightarrow 1.5 \rightarrow 2.0
$$

Observe:

- how the shape of the discharge curve changes;
- how discharge behaves at low storage;
- how discharge behaves at high storage;
- how the equilibrium storage changes.

### Questions

- Why does discharge become more sensitive to storage when **b > 1**?
- How does the position of the equilibrium point change?

<details>
<summary><strong>💡 Show suggested answers</strong></summary>

**Why does discharge become more sensitive to storage when b > 1?**  
Because storage is raised to a power greater than one. At high storage, an additional increase in storage therefore produces a relatively large increase in discharge.

**How does the position of the equilibrium point change?**  
The equilibrium point follows the intersection between the modified discharge curve and the unchanged net-input line. Its exact movement depends on the selected value of b and on the numerical value and units of a.

</details>

---

## Experiment 3 — Change the discharge parameter

Set **b = 1.0** again and compare different values of **a**:

$$
a = 0.005
$$

$$
a = 0.010
$$

$$
a = 0.030
$$

Keep precipitation and evapotranspiration constant.

Observe:

- how the discharge curve moves;
- how the equilibrium point moves;
- whether the equilibrium storage increases or decreases.

### Questions

- What happens to the discharge curve when **a** increases?
- Does the equilibrium storage increase or decrease?
- Which reservoir drains more rapidly?

<details>
<summary><strong>💡 Show suggested answers</strong></summary>

**What happens to the discharge curve when a increases?**  
The discharge curve moves upward. For the same storage, the reservoir produces a larger discharge.

**Does the equilibrium storage increase or decrease?**  
It decreases. A reservoir with a larger discharge parameter requires less storage to release the same net water input.

**Which reservoir drains more rapidly?**  
The reservoir with the larger value of a drains more rapidly.

</details>

---

## Experiment 4 — Change the net water input

Keep **a** and **b** constant.

First increase precipitation **P**, and then increase evapotranspiration **ET**.

Observe how the horizontal line representing the net input **P − ET** moves.

### Questions

- What happens to equilibrium storage when precipitation increases?
- What happens when evapotranspiration increases?
- What does the model predict when **P ≤ ET**?

<details>
<summary><strong>💡 Show suggested answers</strong></summary>

**What happens to equilibrium storage when precipitation increases?**  
The net input increases, so the horizontal line moves upward. A higher storage is generally required for discharge to equal the larger net input.

**What happens when evapotranspiration increases?**  
The net input decreases, so the horizontal line moves downward and the equilibrium storage decreases.

**What does the model predict when P ≤ ET?**  
There is no positive net input available to maintain storage. Without another source of water, the reservoir progressively empties.

</details>

> **Tip:** Change one control at a time. Before moving a slider, predict how the storage or discharge curve should respond, and then compare your prediction with the plotted result.
