"""
MicroGridsPy - Sensitivity Analysis

- In line 25 insert the upper and lower limit of the parameter analysed, as well as the step considered
- Uncomment the parameter to be analysed in line 34-38


"""

import time
from pyomo.environ import  AbstractModel
from Model_Creation import Model_Creation
from Model_Resolution_Brownfield import Model_Resolution_Brownfield
from Model_Resolution_Greenfield import Model_Resolution_Greenfield
from Results import ResultsSummary
import pandas as pd
import numpy as np
from pandas import ExcelWriter

starttt = time.time() 
iteration = 0   
     # Start time counter
sensitivity_results = []
TARIFF = []
sensitivity_index = np.arange(1, 3.01, 0.2)   #the upper bound should have a small increment, otherwise it won't be considere (e.g if the upper bound needed is 3, write 3.01)
for gogle in sensitivity_index:
    start = time.time()         # Start time counter
    model = AbstractModel()     # Define type of optimization problem


    Data_model = "Inputs/Model_data.dat"
    Data_import_model = open(Data_model).readlines()
    
    Data_import_model[26] = '1      {};\n'.format(gogle)   #RES_Specific_Investment_Cost
    #Data_import_model[38] = 'param: Battery_Specific_Investment_Cost := {};              # Specific investment cost of the battery bank [USD/Wh]\n'.format(gogle)
    #Data_import_model[39] = 'param: Battery_Specific_Electronic_Investment_Cost := {};   # Specific investment cost of non-replaceable parts (electronics) of the battery bank [USD/Wh]\n'.format(gogle)
    #Data_import_model[57] = '1      {};\n'.format(gogle)  #Generator_Specific_Investment_Cost
    #Data_import_model[65] = '1      {};\n'.format(gogle)  #Fuel_Specific_Cost

    Data_import_model_write = open(Data_model, 'w').writelines(Data_import_model)


    #%% Input parameters
    Optimization_Goal = 'Operation cost'           # Options: NPC / Operation cost. It allows to switch between a NPC-oriented optimization and a NON-ACTUALIZED Operation Cost-oriented optimization
    MultiObjective_Optimization = 'no'  # yes if optimization of NPC/operation cost and CO2 emissions,no otherwise
    Brownfield_Investment = 0           # 1 if Brownfield investment, 0 Greenfield investment
    Plot_maxCost = 0                    # 1 if the Pareto curve has to include the point at maxNPC/maxOperationCost, 0 otherwise
    Renewable_Penetration = 0          # Fraction of electricity produced by renewable sources. Number from 0 to 1.
    Battery_Independence  = 0           # Number of days of battery independence


    #%% Processing
    Model_Creation(model, Renewable_Penetration, Battery_Independence) # Creation of the Sets, parameters and variables.

    if Brownfield_Investment:
        instance = Model_Resolution_Brownfield(model, Optimization_Goal,MultiObjective_Optimization, Plot_maxCost, Renewable_Penetration, Battery_Independence) # Resolution of the instance
    else:
        instance = Model_Resolution_Greenfield(model, Optimization_Goal,MultiObjective_Optimization, Plot_maxCost, Renewable_Penetration, Battery_Independence) # Resolution of the instance
        
        
    #%% Results
    Results    = ResultsSummary(instance, Optimization_Goal, Brownfield_Investment, gogle, sensitivity_results, TARIFF) 


    #%% Timing
    end = time.time()
    elapsed = end - start
    print('\n\nModel run complete (overall time: ',round(elapsed,0),'s,',round(elapsed/60,1),' m)\n')
    iteration = iteration + 1
    print('\n\nIteration number ', iteration, ' complete\n')

#%%
SENSITIVITY_RESULTS =  pd.DataFrame(sensitivity_results, index = sensitivity_index, columns = ['Investment [kUSD]', 'NPC [kUSD]', 'LCOE [USD/kWh]', 'Fixed cost [kUSD]', 'Variable cost [kUSD]', 'totCO2 [ton]', 'PV panel [kW]', 'Battery [kWh]', 'Generator [kWh]'])    
TARIFF_DF = pd.DataFrame(TARIFF, index = sensitivity_index )
Excel = ExcelWriter('Results/Results_Sensitivity.xlsx')
SENSITIVITY_RESULTS.to_excel(Excel, sheet_name='Costs')
TARIFF_DF.to_excel(Excel, sheet_name='Tariff')
Excel.save()

#%% Timing
enddd = time.time()
elapseddd = enddd - starttt
print('\n\nSensitivity analysis complete (overall time: ',round(elapseddd,0),'s,',round(elapseddd/60,1),' m)\n')
