For complex numerical models, the variance contributions cannot usually be
calculated analytically. They are therefore **estimated from many model
evaluations**.

The basic idea is simple:

1. sample many parameter combinations across the full parameter space;
2. run the model for those combinations;
3. compare how the model output changes;
4. estimate the fraction of output variance associated with each parameter
   alone and with its interactions.
