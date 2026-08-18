The exercise uses one fixed synthetic precipitation time series as model input and simulates nonlinear reservoir discharge as model output. Two model parameters are treated as uncertain: 
- **k** controls the magnitude of reservoir drainage,
- **b** controls the nonlinearity of the storage-discharge relationship.

At every time step, precipitation first enters the reservoir storage. The model then calculates discharge and updates the remaining storage using the equations shown below.
