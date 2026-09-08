- Sobol' analysis decomposes the variance of a model output into contributions
  from individual parameters and their interactions.

- The **first-order index $S_i$** is the fraction of output variance associated
  with parameter $i$ acting alone.

- The **total-order index $S_{T_i}$** includes the individual effect and every
  interaction involving parameter $i$.

- For independent inputs, $S_{T_i}-S_i$ summarizes the interaction
  contributions involving parameter $i$.

- The app estimates the indices by comparing model evaluations from two base
  sample matrices and parameter-specific hybrid matrices.

- A low-discrepancy sampling sequence is used so that the parameter space is
  covered efficiently and the teaching example remains numerically stable.

- The sample size $N$ should be increased until the estimated indices are
  reasonably stable.

- Compared with Morris, Sobol' provides a quantitative decomposition of output
  variance, but it requires substantially more model evaluations.
