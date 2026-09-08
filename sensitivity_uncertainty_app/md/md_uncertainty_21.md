- **Sensitivity analysis and parameter uncertainty answer different questions.**
  Sensitivity analysis asks which parameters influence the model output;
  parameter uncertainty asks how incomplete knowledge of parameter values affects
  model predictions.

- **Parameter uncertainty is propagated through the forward model.** Sampling
  several plausible parameter sets produces an ensemble of model realizations.

- **Equifinality means that several parameter combinations may reproduce the
  observations similarly well.** A single best-performing parameter set does not
  necessarily imply that the parameters are uniquely identified.

- **GLUE is an ensemble-based uncertainty approach.** It samples parameter sets,
  runs the model, evaluates model behaviour, and retains parameter sets that meet
  a chosen behavioural criterion.

- **Behavioural and non-behavioural classifications depend on modelling choices.**
  The parameter ranges, likelihood or performance measure, threshold and
  weighting scheme must therefore be stated and justified.

- **Predictive uncertainty is described by the spread of the retained model
  ensemble.** Quantiles or uncertainty bands can be used to summarize this spread.

- The uncertainty shown in the synthetic GLUE example is specifically
  **parameter-induced predictive uncertainty**. It does not include input,
  structural or observation uncertainty.
