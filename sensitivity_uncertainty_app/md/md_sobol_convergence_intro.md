The Sobol' indices are estimated from a finite number of sampled parameter
combinations.

The number of samples $N$ controls how extensively the parameter space is
explored. Increasing $N$ requires more model evaluations, but usually gives
more stable estimates.

A simple convergence check asks:

**Do the estimated sensitivity indices stop changing substantially when $N$
is increased?**

The plot below follows one selected parameter and shows how its estimated
first-order and total-order indices change as more samples are used.
