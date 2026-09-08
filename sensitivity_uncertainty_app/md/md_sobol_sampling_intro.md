The theoretical Sobol' indices are estimated by sampling the parameter space
and repeatedly running the model.

The calculation starts from two base sample matrices, $A$ and $B$. Each matrix
has $N$ rows and $k$ columns, each row represents one complete parameter set while each column the values for a specific parameter.

For this teaching example, the app uses a **low-discrepancy Sobol sequence** to
sample the parameter space. Low-discrepancy sampling covers the parameter space
more evenly than ordinary pseudo-random sampling and gives much more stable
estimates at modest sample sizes.

The diagram below shows one conceptual row of $A$, $B$, and the hybrid matrix
used for one parameter.
