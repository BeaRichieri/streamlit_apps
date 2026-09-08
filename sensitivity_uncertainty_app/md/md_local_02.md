For parameter $x_i$, a local finite-difference sensitivity can be approximated by

$$
S_i(x^*) \approx \frac{f(x^*+\Delta x_i e_i)-f(x^*-\Delta x_i e_i)}{2\Delta x_i}
$$

**Inside the parameter domain**, sensitivity is approximated using a **central finite difference**. **Close to the parameter boundaries**, where a symmetric perturbation is not possible, a **forward or backward finite difference** is used instead.

The value therefore describes the **local slope** of the model response around the selected reference point $x^*$.
