For each row $j=1,\ldots,N$, let

$$
f(A_j), \qquad f(B_j), \qquad f(C_{i,j})
$$

be the corresponding model outputs.

The page uses the following Monte Carlo estimators.

**First-order index**

$$
\widehat{S}_i
=
\frac{
\frac{1}{N}
\sum_{j=1}^{N}
f(B_j)
\left[
f(C_{i,j})-f(A_j)
\right]
}{
\widehat{\mathrm{Var}}(Y)
}.
$$

**Total-order index**

$$
\widehat{S}_{T_i}
=
\frac{
\frac{1}{2N}
\sum_{j=1}^{N}
\left[
f(A_j)-f(C_{i,j})
\right]^2
}{
\widehat{\mathrm{Var}}(Y)
}.
$$

The first expression is a Saltelli-type first-order estimator. The second is
the Jansen total-order estimator.
