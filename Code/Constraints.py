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

                                                                                                                                        
                                                                 
#%% Economic constraints

"Objective function"
def Net_Present_Cost(model):
    return (sum(model.Scenario_Net_Present_Cost[s]*model.Scenario_Weight[s] for s in model.scenario))

def Scenario_Net_Present_Cost(model,s): 
    return model.Scenario_Net_Present_Cost[s] == model.Total_Investment_Cost + model.Fixed_Costs + model.Variable_Costs[s]


"Investment cost"
def Total_Investment_Cost(model):
    return model.Total_Investment_Cost == model.RES_Investment_Cost + model.BESS_Investment_Cost + model.Generator_Investment_Cost + sum(model.SC_Investment_Cost[c] + model.Boiler_Investment_Cost[c] + model.Tank_Investment_Cost[c] + model.Electric_Resistance_Investment_Cost[c] for c in model.classes)

def RES_Investment_Cost(model):
   return model.RES_Investment_Cost == model.RES_Units*model.RES_Nominal_Capacity*model.RES_Inv_Specific_Cost

def SC_Investment_Cost(model,c):
   return model.SC_Investment_Cost[c] == model.SC_Units[c]*model.SC_Nominal_Capacity*model.SC_Inv_Specific_Cost

def BESS_Investment_Cost(model):
   return model.BESS_Investment_Cost == model.BESS_Nominal_Capacity*model.BESS_Inv_Specific_Cost

def Generator_Investment_Cost(model):
   return model.Generator_Investment_Cost == model.Generator_Nominal_Capacity*model.Generator_Inv_Specific_Cost

def Boiler_Investment_Cost(model,c):
   return model.Boiler_Investment_Cost[c] == model.Boiler_Nominal_Capacity[c]*model.Boiler_Inv_Specific_Cost

def Tank_Investment_Cost(model,c):
   return model.Tank_Investment_Cost[c] == model.Tank_Nominal_Capacity[c]*model.Tank_Inv_Specific_Cost

def Electric_Resistance_Investment_Cost(model,c):
   return model.Electric_Resistance_Investment_Cost[c] == model.Electric_Resistance_Nominal_Power[c]*model.Electric_Resistance_Specific_Inv_Cost


"Fixed costs"                                                  
def Fixed_Costs(model):
    return model.Fixed_Costs == model.RES_OM_Cost + model.BESS_OM_Cost + model.BESS_Replacement_Cost + model.Generator_OM_Cost + sum(model.SC_OM_Cost[c] + model.Boiler_OM_Cost[c] + model.Tank_OM_Cost[c] + model.Electric_Resistance_OM_Cost[c] for c in model.classes)
 
def RES_OM_Cost(model):
    return model.RES_OM_Cost == sum(((model.RES_Investment_Cost*model.RES_OM_Specific_Cost)/((1+model.Discount_Rate)**model.Project_Years[y])) for y in model.years)

def SC_OM_Cost(model,c):
    return model.SC_OM_Cost[c] == sum(((model.SC_Investment_Cost[c]*model.SC_OM_Specific_Cost)/((1+model.Discount_Rate)**model.Project_Years[y])) for y in model.years)

def BESS_OM_Cost(model):
    return model.BESS_OM_Cost == sum(((model.BESS_Investment_Cost*model.BESS_OM_Specific_Cost)/((1+model.Discount_Rate)**model.Project_Years[y])) for y in model.years)

def BESS_Replacement_Cost(model):
    return model.BESS_Replacement_Cost == model.BESS_Investment_Cost/((1+model.Discount_Rate)**model.BESS_Replacement_Time)

def Generator_OM_Cost(model):
    return model.Generator_OM_Cost == sum(((model.Generator_Investment_Cost*model.Generator_OM_Specific_Cost)/((1+model.Discount_Rate)**model.Project_Years[y])) for y in model.years)

def Boiler_OM_Cost(model,c):
    return model.Boiler_OM_Cost[c] == sum(((model.Boiler_Investment_Cost[c]*model.Boiler_OM_Specific_Cost)/((1+model.Discount_Rate)**model.Project_Years[y])) for y in model.years)

def Tank_OM_Cost(model,c):
    return model.Tank_OM_Cost[c] == sum(((model.Tank_Investment_Cost[c]*model.Tank_OM_Specific_Cost)/((1+model.Discount_Rate)**model.Project_Years[y])) for y in model.years)

def Electric_Resistance_OM_Cost(model,c):
    return model.Electric_Resistance_OM_Cost[c] == sum(((model.Electric_Resistance_Investment_Cost[c]*model.Electric_Resistance_OM_Specific_Cost)/((1+model.Discount_Rate)**model.Project_Years[y])) for y in model.years)


"Variable costs"
def Variable_Costs(model,s):
    return model.Variable_Costs[s] == model.Scenario_Lost_Load_Cost_EE[s] + model.Total_Diesel_Cost[s] + sum(model.Scenario_Lost_Load_Cost_Th[s,c] + model.Total_NG_Cost[s,c] for c in model.classes)
                                                                                      
def Scenario_Lost_Load_Cost_EE(model,s):
    foo=[]
    for f in range(1,model.Periods+1):
        foo.append((s,f))
    return  model.Scenario_Lost_Load_Cost_EE[s] == sum(((sum(model.Lost_Load_EE[s,t]*model.EE_Value_Of_Lost_Load/60 for s,t in foo))/((1+model.Discount_Rate)**model.Project_Years[y])) for y in model.years) 

def Total_Diesel_Cost(model,s):
    foo=[]
    for f in range(1,model.Periods+1):
        foo.append((s,f))
    return model.Total_Diesel_Cost[s] == sum(((sum(model.Diesel_Consumption[s,t]*model.Diesel_Unitary_Cost for s,t in foo))/((1+model.Discount_Rate)**model.Project_Years[y])) for y in model.years) 
    
def Scenario_Lost_Load_Cost_Th(model,s,c):
    foo=[] 
    for f in range(1,model.Periods+1):
        foo.append((s,f))
    return  model.Scenario_Lost_Load_Cost_Th[s,c] == sum(((sum(model.Lost_Load_Th[s,c,t]*model.Th_Value_Of_Lost_Load/60 for s,t in foo))/((1+model.Discount_Rate)**model.Project_Years[y])) for y in model.years) 

def Total_NG_Cost(model,s,c):
    foo=[] 
    for f in range(1,model.Periods+1):
        foo.append((s,f))
    return  model.Total_NG_Cost[s,c] == sum(((sum(model.NG_Consumption[s,c,t]*model.NG_Unitary_Cost for s,t in foo))/((1+model.Discount_Rate)**model.Project_Years[y])) for y in model.years)

    
  
#%% Electricity generation system constraints 

def Electric_Energy_Balance(model,s,t):
    return model.Electric_Energy_Demand[s,t] + sum(model.Electric_Resistance_Energy_Consumption[s,c,t] for c in model.classes) == model.RES_Energy_Production[s,t] - model.BESS_Inflow[s,t] + model.BESS_Outflow[s,t] + model.Generator_Energy_Production[s,t] + model.Lost_Load_EE[s,t] - model.Electric_Curtailment[s,t]

"Renewable Energy Sources constraints"
def RES_Energy_Production(model,s,t):
    return model.RES_Energy_Production[s,t] == model.RES_Unit_Energy_Production[s,t]*model.RES_Inverter_Efficiency*model.RES_Units

"Battery Energy Storage constraints"
def BESS_State_of_Charge(model,s,t):
    if t==1:
        return model.BESS_State_of_Charge[s,t] == model.BESS_Nominal_Capacity - model.BESS_Outflow[s,t]/60/model.BESS_Discharge_Efficiency + model.BESS_Inflow[s,t]/60*model.BESS_Charge_Efficiency
    if t>1:  
        return model.BESS_State_of_Charge[s,t] == model.BESS_State_of_Charge[s,t-1] - model.BESS_Outflow[s,t]/60/model.BESS_Discharge_Efficiency + model.BESS_Inflow[s,t]/60*model.BESS_Charge_Efficiency    

def Maximum_BESS_Charge(model,s,t):
    return model.BESS_State_of_Charge[s,t] <= model.BESS_Nominal_Capacity

def Minimum_BESS_Charge(model,s,t):
    return model.BESS_State_of_Charge[s,t] >= model.BESS_Nominal_Capacity*model.BESS_Depth_of_Discharge

def Max_Power_BESS_Charge(model): 
    return model.Maximum_BESS_Charge_Power == model.BESS_Nominal_Capacity/(model.BESS_Maximum_Charge_Time)

def Max_Power_BESS_Discharge(model):
    return model.Maximum_BESS_Discharge_Power == model.BESS_Nominal_Capacity/(model.BESS_Maximum_Discharge_Time)

def Max_BESS_Inflow(model,s,t):
    return model.BESS_Inflow[s,t] <= model.Maximum_BESS_Charge_Power

def Min_BESS_Outflow(model,s,t):
    return model.BESS_Outflow[s,t] <= model.Maximum_BESS_Discharge_Power

"Diesel generator constraints"
def Maximum_Generator_Energy(model,s,t):
    return model.Generator_Energy_Production[s,t] <= model.Generator_Nominal_Capacity

def Diesel_Consumption(model,s,t): 
    return model.Diesel_Consumption[s,t] == model.Generator_Energy_Production[s,t]/model.Generator_Efficiency/model.Lower_Heating_Value/60

"Lost Load constraints"
def Maximum_Lost_Load_EE(model,s):
    return model.EE_Lost_Load_Tolerance >= (sum(model.Lost_Load_EE[s,t] for t in model.periods)/sum(model.Electric_Energy_Demand[s,t] for t in model.periods))


#%% Thermal energy generation system constraints

def Thermal_Energy_Balance(model,s,c,t):
     return  model.Thermal_Energy_Demand[s,c,t] == model.SC_Energy_Production[s,c,t] + model.Electric_Resistance_Energy_Production[s,c,t] - model.Tank_Inflow[s,c,t] + model.Tank_Outflow[s,c,t] +  model.Boiler_Energy_Production[s,c,t] - model.Thermal_Energy_Curtailment[s,c,t] + model.Lost_Load_Th[s,c,t]

"Solar collector constraints"
def SC_Energy_Production(model,s,c,t):
    return model.SC_Energy_Production[s,c,t] == model.SC_Unit_Energy_Production[s,c,t]*model.SC_Units[c]

"Boiler constraints"
def Maximum_Boiler_Energy(model,s,c,t):   
    return model.Boiler_Energy_Production[s,c,t] <= model.Boiler_Nominal_Capacity[c]

def NG_Consumption(model,s,c,t):
    return model.NG_Consumption[s,c,t] == model.Boiler_Energy_Production[s,c,t]/model.Boiler_Efficiency/model.Lower_Heating_Value_NG/60

"Tank constraints"
def Tank_State_of_Charge(model,s,c,t):
    if t==1:
        return model.Tank_State_of_Charge[s,c,t] == model.Tank_Nominal_Capacity[c] + model.SC_Energy_Production[s,c,t]/60 + model.Electric_Resistance_Energy_Production[s,c,t]*model.Electric_Resistance_Efficiency/60- model.Tank_Outflow[s,c,t]/60
    if t>1:  
        return model.Tank_State_of_Charge[s,c,t] == model.Tank_State_of_Charge[s,c,t-1]*model.Tank_Efficiency + model.SC_Energy_Production[s,c,t]/60 + model.Electric_Resistance_Energy_Production[s,c,t]*model.Electric_Resistance_Efficiency/60- model.Tank_Outflow[s,c,t]/60

def Maximum_Tank_Charge(model,s,c,t):
    return model.Tank_State_of_Charge[s,c,t] <= model.Tank_Nominal_Capacity[c]

def Minimum_Tank_Charge(model,s,c,t):
    return model.Tank_State_of_Charge[s,c,t] >= model.Tank_Nominal_Capacity[c]*model.Tank_Depth_of_Discharge

def Max_Power_Tank_Discharge(model,c):
    return model.Maximum_Tank_Discharge_Power[c] == model.Tank_Nominal_Capacity[c]/model.Tank_Maximum_Discharge_Time

def Min_Tank_Outflow(model,s,c,t):
    return model.Tank_Outflow[s,c,t] <= model.Maximum_Tank_Discharge_Power[c]

"Electric resistance constraints"
def Maximum_Electric_Resistance_Energy(model,s,c,t):
    return model.Electric_Resistance_Energy_Production[s,c,t] <= model.Electric_Resistance_Nominal_Power[c]

def Electric_Resistance_Energy_Production(model,s,c,t):
    return model.Electric_Resistance_Energy_Production[s,c,t] == model.Electric_Resistance_Energy_Consumption[s,c,t]*model.Electric_Resistance_Efficiency

def Tot_Electric_Resistance_Energy_Production(model,s,t):
    return model.Tot_Electric_Resistance_Energy_Production[s,t] == sum(model.Electric_Resistance_Energy_Production[s,c,t] for c in model.classes)
    
"Lost load constraints"
def Maximum_Lost_Load_Th(model,s,c):
    return model.Th_Lost_Load_Tolerance*sum(model.Thermal_Energy_Demand[s,c,t] for t in model.periods) >= sum(model.Lost_Load_Th[s,c,t] for t in model.periods)
