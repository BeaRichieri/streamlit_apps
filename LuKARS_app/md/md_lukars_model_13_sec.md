The **secondary spring discharge** $Q_{\mathrm{sec},i,t}$ (m³/$\Delta t$) represents water that leaves hydrotope $i$ directly through a secondary outlet and therefore does not contribute to the matrix, conduit, or simulated discharge of the main spring.

It becomes active only when the hydrotope storage exceeds the hydrotope-specific threshold $E_{\mathrm{sec},i}$. Above this threshold, the discharge increases linearly with the excess storage.

**Symbols in this equation**

| Symbol | Unit | Interpretation |
|---|---:|---|
| 🔵 $k_{\mathrm{sec},i}$ | $1/\Delta t$ | Discharge coefficient controlling how rapidly excess hydrotope storage is released as secondary spring discharge. |
| $E_{i,t}$ | mm | Water level (storage depth) in hydrotope $i$. |
| 🔵 $E_{\mathrm{sec},i}$ | mm | Storage threshold above which secondary spring discharge becomes active. |
| $A_i$ | m² | Area represented by hydrotope $i$. |

