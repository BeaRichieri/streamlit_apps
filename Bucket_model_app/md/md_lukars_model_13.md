$\varepsilon_{i,t}$ is a **dimensionless activation indicator** that carries the activation state of the fast-flow pathway from one time step to the next.

The hysteresis mechanism is defined as follows:

- if the pathway is inactive ($\varepsilon_{i,t}=0$), it remains inactive while $E_{i,t+1}<E_{\max,i}$ and activates when $E_{i,t+1}\geq E_{\max,i}$;
- if the pathway is active ($\varepsilon_{i,t}=1$), it remains active while $E_{i,t+1}>E_{\min,i}$ and deactivates when $E_{i,t+1}\leq E_{\min,i}$.

Because $E_{\max,i} > E_{\min,i}$, activation and deactivation occur at different storage values. This hysteresis prevents rapid switching around a single threshold and allows fast flow to remain active during the falling limb until the lower threshold is reached.

$\varepsilon_{i,t}$ is a **state variable**, not a calibrated model parameter.
