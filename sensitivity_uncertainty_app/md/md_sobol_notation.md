The same indices can also be written using conditional expectations.

**First order**

$$
S_i=
\frac{
\mathrm{Var}_{X_i}
\left[
\mathbb{E}(Y\mid X_i)
\right]
}{
\mathrm{Var}(Y)
}.
$$

**Total order**

$$
S_{T_i}
=
1-
\frac{
\mathrm{Var}_{X_{\sim i}}
\left[
\mathbb{E}(Y\mid X_{\sim i})
\right]
}{
\mathrm{Var}(Y)
}.
$$

The notation means:

- $\mathbb{E}$ = **expected value**, i.e. an average;
- $\mathrm{Var}$ = **variance**, i.e. how strongly a quantity varies around
  its mean;
- $X_i$ = the parameter being investigated;
- $X_{\sim i}$ = **all parameters except $X_i$**.

For learning the method, the variance-decomposition interpretation above is
usually easier: $S_i$ is the individual contribution, whereas $S_{T_i}$
includes the individual contribution plus interactions.
