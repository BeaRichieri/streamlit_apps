$Q_{\mathrm{hyd},i,t}$ (m³/$\Delta t$) is the **fast flow from hydrotope $i$ toward the conduit**.

Fast hydrotope flow is activated only when the hydrotope storage is sufficiently high.

The dimensionless activation indicator $\varepsilon_{i,t}$ determines whether the fast-flow pathway is active ($\varepsilon=1$) or inactive ($\varepsilon=0$). The thresholds $E_{\min,i}$ and $E_{\max,i}$ define its hysteretic activation and deactivation, while the exponent $\alpha_i$ and the scaling parameters $k_{\mathrm{hyd},i}$ and $l_{\mathrm{hyd},i}$ control the magnitude of fast flow.

**Symbols in this equation**

| Symbol | Unit | Interpretation |
|---|---:|---|
| $\varepsilon_{i,t}$ | – | Dimensionless connectivity/activation indicator: $0$ when the fast-flow pathway is inactive and $1$ when it is active. Its state is controlled by the hysteresis between $E_{\max,i}$ and $E_{\min,i}$. |
| $E_{i,t}$ | mm | Water level (storage depth) in hydrotope $i$. |
| 🔵 $E_{\min,i}$ | mm | Lower storage threshold. Once fast flow is active, it deactivates when storage reaches or falls below this value. |
| 🔵 $E_{\max,i}$ | mm | Upper storage threshold for activating fast hydrotope flow. |
| 🔵 $\alpha_i$ | – | Dimensionless exponent controlling the nonlinearity of the fast-flow response. |
| 🔵 $k_{\mathrm{hyd},i}$ | m²/$\Delta t$ | Discharge coefficient scaling the magnitude of fast hydrotope flow. |
| $l_{\mathrm{hyd},i}$ | m | Mean distance of hydrotope $i$ from the spring; it appears in the denominator of the fast-flow term. |
| $A_i$ | m² | Area represented by hydrotope $i$. |
