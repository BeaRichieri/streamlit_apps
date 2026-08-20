The Kerschbaum configuration defines **three hydrotopes** with fixed areas and characteristic flow lengths. The slider limits are read directly from the supplied configuration file.

The parameters of different hydrotopes are treated **independently** in this teaching interface. For example, a parameter value for Hydrotope 1 is not required to be smaller or larger than the corresponding value for Hydrotope 2 or 3.

The only retained parameter constraint is the physically required hysteresis condition:

$E_{\max,i} > E_{\min,i}$

for each individual hydrotope.

The initial slider values are the midpoints of the configured ranges; geometric midpoints are used for parameters whose original calibration formulation used logarithmic transformation.
