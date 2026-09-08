The synthetic model uses the same core response as the Local sensitivity and
Morris examples:

$$
Y=
2x_1+
1.5x_1^2+
0.2x_2+
2\sin(\pi x_3)
+
\gamma (x_1-0.5)(x_3-0.5).
$$

All three parameters vary **independently** between 0 and 1.

The final term creates a **interaction between $x_1$ and $x_3$**:

$$
\gamma (x_1-0.5)(x_3-0.5).
$$

- With $\gamma=0$, the model is additive and there is no $x_1$-$x_3$
  interaction.
- Increasing $\gamma$ strengthens that interaction.

**$N$** is the **number of samples** and controls how densely the parameter space is sampled.
