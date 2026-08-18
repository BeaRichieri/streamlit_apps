A hydrological model can be used in two complementary directions.

In a **forward problem**, the model structure, forcing data, initial/boundary conditions and parameter values are specified. The model is then evaluated to calculate the simulated response. In LuKARS, this means providing precipitation $P(t)$ and other forcing data (e.g., $ET(t)$) together with a parameter vector $x$ and computing simulated spring discharge and internal model states.

In an **inverse problem**, observations are used to infer unknown quantities of the model, most commonly parameter values. Parameter estimation therefore requires repeated forward model evaluations, comparison with observations, and a rule for updating or selecting parameter sets.

The two ideas are linked: **inverse modelling is built on repeated forward modelling**.
