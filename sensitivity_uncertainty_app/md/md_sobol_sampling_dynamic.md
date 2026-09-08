To estimate the sensitivity of **[[PARAMETER]]**, the code creates a hybrid
matrix $C_{[[INDEX]]}$.

$C_{[[INDEX]]}$ starts as a copy of $A$, but the column corresponding to
**[[PARAMETER]]** is replaced by the same column from $B$.

The model is therefore evaluated for:

- the original parameter combinations in $A$;
- the independent combinations in $B$;
- the hybrid combinations in $C_{[[INDEX]]}$.

Comparing their model outputs isolates the effect of changing the selected
parameter while the remaining parameter values are controlled through the
sampling design.
