# Unsteady-state reservoir experiments

Use the experiments below to investigate the behaviour of the conceptual reservoir.

Modify the sliders in the **unsteady-state interactive plot** in the original app tab.  
For a clear comparison, change **only one parameter at a time** and observe how the result changes.

## Experiment 1 — Response to one precipitation event

Select **Single precipitation event** and begin with approximately:

$$
P_{\max} = 8\ \mathrm{mm\,day^{-1}}
$$

$$
S_0 = 5\ \mathrm{mm}
$$

$$
a = 0.010
$$

$$
b = 1.0
$$

$$
ET = 0.3\ \mathrm{mm\,day^{-1}}
$$

Observe the sequence of changes in precipitation, storage and discharge.

### Questions

- Does storage respond immediately to precipitation?
- When does discharge begin to increase?
- Is maximum discharge reached before, during or after the precipitation maximum?
- What happens after precipitation stops?

<details>
<summary><strong>💡 Show suggested answers</strong></summary>

**Does storage respond immediately to precipitation?**  
Yes. Precipitation immediately adds water to the reservoir. Storage increases when the input exceeds the combined losses through evapotranspiration and discharge.

**When does discharge begin to increase?**  
Discharge begins to increase as soon as storage rises because it is calculated from the current storage.

**When is maximum discharge reached relative to maximum precipitation?**  
Maximum discharge is generally delayed relative to maximum precipitation because precipitation must first increase reservoir storage.

**What happens after precipitation stops?**  
Storage decreases because water continues to leave through discharge and evapotranspiration. Discharge therefore declines during the recession.

</details>

---

## Experiment 2 — Slow and fast drainage

Keep all other values unchanged and compare:

$$
a = 0.005
$$

$$
a = 0.010
$$

$$
a = 0.030
$$

Observe:

- the maximum storage;
- the maximum discharge;
- the duration of the recession;
- the time required for the reservoir to empty.

### Questions

- Which value of **a** produces the highest storage?
- Which value produces the strongest discharge response?
- Which reservoir retains water for the longest time?

<details>
<summary><strong>💡 Show suggested answers</strong></summary>

**Which value of a produces the highest storage?**  
The smallest value of a generally produces the highest storage because water is released more slowly.

**Which value produces the strongest discharge response?**  
The largest value of a produces a stronger and more rapid discharge response for the same storage.

**Which reservoir retains water for the longest time?**  
The reservoir with the smallest value of a retains water for the longest time and has the slowest recession.

</details>

---

## Experiment 3 — Linear and nonlinear response

Return to **a = 0.010** and gradually increase **b**:

$$
b = 1.0 \rightarrow 1.5 \rightarrow 2.0
$$

Observe how the discharge response changes during both the rising and falling parts of the event.

### Questions

- How does increasing **b** affect discharge when storage is low?
- How does it affect discharge when storage is high?
- Does the nonlinear reservoir produce a sharper discharge peak?

<details>
<summary><strong>💡 Show suggested answers</strong></summary>

**How does increasing b affect discharge when storage is low?**  
For the values used in this demonstration, discharge can remain relatively weak at low storage when the response is strongly nonlinear.

**How does increasing b affect discharge when storage is high?**  
Discharge increases much more rapidly at high storage because storage is raised to a larger exponent.

**Does the nonlinear reservoir produce a sharper discharge peak?**  
It can produce a sharper response when storage becomes high. The exact comparison also depends on the selected value and units of a.

</details>

---

## Experiment 4 — Antecedent storage

Keep the precipitation scenario and model parameters constant, but compare different initial storage values:

$$
S_0 = 0\ \mathrm{mm}
$$

$$
S_0 = 5\ \mathrm{mm}
$$

$$
S_0 = 15\ \mathrm{mm}
$$

### Questions

- How does initial storage influence peak discharge?
- Does a wet reservoir respond differently from an initially empty one?
- Why is antecedent storage important when modelling flood response?

<details>
<summary><strong>💡 Show suggested answers</strong></summary>

**How does initial storage influence peak discharge?**  
Higher initial storage generally produces a larger and earlier discharge response because the reservoir already contains water when precipitation begins.

**Does a wet reservoir respond differently from an empty one?**  
Yes. A wet reservoir requires less additional precipitation to reach storage levels associated with high discharge.

**Why is antecedent storage important when modelling flood response?**  
It represents the wetness of the system before an event. The same precipitation event can therefore produce very different responses under dry and wet conditions.

</details>

---

## Experiment 5 — Multiple precipitation events

Compare the following synthetic precipitation scenarios:

- **Single precipitation event**
- **Two precipitation events**
- **Repeated precipitation events**

Keep **a**, **b**, **ET** and the maximum precipitation rate unchanged.

Observe whether the reservoir has enough time to drain between precipitation events.

### Questions

- What happens when a new precipitation event occurs while storage is still elevated?
- Does the second event generate the same discharge peak as the first?
- Under which conditions does storage accumulate between events?

<details>
<summary><strong>💡 Show suggested answers</strong></summary>

**What happens when a new precipitation event occurs while storage is still elevated?**  
The new precipitation is added to an already wet reservoir, so storage and discharge can rise more rapidly.

**Does the second event generate the same discharge peak as the first?**  
Not necessarily. If the reservoir has not drained completely, the second event can generate a larger discharge peak even when its precipitation intensity is similar.

**Under which conditions does storage accumulate between events?**  
Storage accumulates when the time between events is too short for discharge and evapotranspiration to remove the previously stored water.

</details>

> **Tip:** Change one control at a time. Before moving a slider, predict how the storage or discharge curve should respond, and then compare your prediction with the plotted result.
