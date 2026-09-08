**What does $S_{T_i}-S_i$ mean?**

Because the parameters in this example are independent, the difference $$S_{T_i}-S_i$$ is the sum of the Sobol' interaction contributions involving parameter $i$.

For three parameters, for example,

$$
S_{T_1}-S_1
=
S_{12}+S_{13}+S_{123}.
$$

A value close to zero therefore indicates weak interactions involving that
parameter. A larger value indicates stronger interactions.

The interaction gap should **not** be summed across parameters, because the same
interaction appears in the total-order index of every parameter involved in
that interaction.
