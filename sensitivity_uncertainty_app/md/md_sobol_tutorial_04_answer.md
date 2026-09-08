Yes. Both methods identify **$x_2$ as weakly influential** for this synthetic model.

The difference is in the information they provide:

- **Morris** is mainly a screening method: it efficiently ranks parameters and can flag nonlinear or interacting behaviour.
- **Sobol'** quantitatively attributes fractions of the output variance to individual parameters and, through total-order indices, to their interactions.

Sobol' therefore provides a more quantitative variance decomposition, but at a higher computational cost.
