"""
Multi-Energy System (MESpy) model

Modelling framework for optimization of hybrid electric and thermal small-scale energy systems sizing

Authors: 
    Stefano Pistolese - Department of Energy, Politecnico di Milano, Milan, Italy
    Nicolò Stevanato  - Department of Energy, Politecnico di Milano, Milan, Italy
                        Fondazione Eni Enrico Mattei, Milan, Italy
    Lorenzo Rinaldi   - Department of Energy, Politecnico di Milano, Milan, Italy
    Sergio Balderrama - Department of Mechanical and Aerospace Engineering, University of Liège, Liège, Belgium
                        San Simon University, Centro Universitario de Investigacion en Energia, Cochabamba, Bolivia
"""


import pandas as pd


#%%
def Initialize_years(model,i):
    '''
    This function returns the value of each year of the project.     
    :param model: Pyomo model as defined in the Model_Creation script.  
    :return: The year i.
    '''    
    return i


#%% Electricity demand
Electric_Energy_Demand = pd.read_csv('Inputs/Electric_Demand.csv', sep=';', index_col=0) # Import electricity demand
Electric_Energy_Demand = Electric_Energy_Demand.round(3)

def Initialize_Electric_Energy_Demand(model,i,t):
    '''
    This function returns the value of the energy demand from a system for each period of analysis from a excel file.
    :param model: Pyomo model as defined in the Model_Creation script.    
    :return: The energy demand for the period t.         
    '''
    return float(Electric_Energy_Demand.iloc[t-1,i-1])


#%% Thermal energy demand
Thermal_Energy_Demand = pd.read_csv('Inputs/Thermal_Demand.csv', sep=';',  index_col=0) # Import thermal energy demand
Thermal_Energy_Demand = Thermal_Energy_Demand.round(3)

def Initialize_Thermal_Energy_Demand(model,i,c,t):
    '''
    This function returns the value of the thermal energy demand from a system for each period and classes of analysis from a excel file.
    :param model: Pyomo model as defined in the Model_Creation script.
    :return: The energy demand for the period t.     
    '''
    column=i*c
    return float(Thermal_Energy_Demand.iloc[t-1,column-1])


#%% PV output
RES_Energy_Output = pd.read_csv('Inputs/RES_Energy_Output.csv', sep=';', index_col=0)  # Import RES energy generation profile
RES_Energy_Output = RES_Energy_Output.round(3)

def Initialize_RES_Energy(model, i, t):
    '''
    This function returns the value of the energy yield by one PV under the characteristics of the system 
    analysis for each period of analysis from a excel file.
    :param model: Pyomo model as defined in the Model_Creation script.
    :return: The energy yield of one PV for the period t.
    '''
    return float(RES_Energy_Output.iloc[t-1,i-1])


#%% Solar collector output
SC_Energy_Output = pd.read_csv('Inputs/SC_Energy_Output.csv', sep=';', index_col=0)  # Import solar collector energy generation profile
SC_Energy_Output = SC_Energy_Output.round(3)

def Initialize_SC_Energy(model,i,c,t):
    '''
    This function returns the value of the thermal energy demand from a system for each period and classes of analysis from a excel file.
    :param model: Pyomo model as defined in the Model_Creation script.
    :return: The energy demand for the period t.     
    '''
    column=i*c
    return float(SC_Energy_Output.iloc[t-1,column-1])


#%%
def Marginal_Cost_Generator_1(model):
    return model.Diesel_Cost/(model.Lower_Heating_Value*model.Generator_Effiency)


#%%
def Start_Cost(model): 
    return model.Marginal_Cost_Generator_1*model.Generator_Nominal_Capacity*model.Cost_Increase


#%%
def Marginal_Cost_Generator(model):
    return (model.Marginal_Cost_Generator_1*model.Generator_Nominal_Capacity-model.Start_Cost_Generator)/model.Generator_Nominal_Capacity 

