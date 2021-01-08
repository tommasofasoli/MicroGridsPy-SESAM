"""
Multi-Energy System (MESpy) model

Modelling framework for optimization of hybrid electric and thermal small-scale energy systems sizing

Authors: 
    Lorenzo Rinaldi   - Department of Energy, Politecnico di Milano, Milan, Italy
    Stefano Pistolese - Department of Energy, Politecnico di Milano, Milan, Italy
    Nicolò Stevanato  - Department of Energy, Politecnico di Milano, Milan, Italy
                        Fondazione Eni Enrico Mattei, Milan, Italy
    Sergio Balderrama - Department of Mechanical and Aerospace Engineering, University of Liège, Liège, Belgium
                        San Simon University, Centro Universitario de Investigacion en Energia, Cochabamba, Bolivia
"""

import time
start = time.time()
    
from pyomo.environ import AbstractModel
from Results import TimeSeries, EnergySystemInfo
from Model_Creation import Model_Creation
from Model_Resolution import Model_Resolution
from Plots import ElectricLoadCurves,ThermalLoadCurves,ElectricDispatch,ThermalDispatch

model = AbstractModel()  # Define type of optimization problem

#%% Optimization model
Model_Creation(model)  # Creation of the Sets, parameters and variables.
instance = Model_Resolution(model)  # Resolution of the instance

#%% Result export
TimeSeries = TimeSeries(instance)  # Extract the results of energy from the instance and save it in a excel file 
EnergySystemSize,EnergySystemCost,EnergyIndicators = EnergySystemInfo(instance)

#%% Plot
# ElectricLoadCurves(instance)
# ThermalLoadCurves(instance)
# ElectricDispatch(instance,TimeSeries)
# ThermalDispatch(instance,TimeSeries)

    

end = time.time()
elapsed = end - start
print("\nTime: ",round(elapsed/60,0),"min")

