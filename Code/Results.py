
import pandas as pd
import warnings; warnings.simplefilter(action='ignore', category=FutureWarning)


#%% Results summary
def ResultsSummary(instance, Optimization_Goal, Brownfield_Investmen, gogle, sensitivity_results, TARIFF):

    #%% Importing parameters
    P  = int(instance.Periods.extract_values()[None])
    Y  = int(instance.Years.extract_values()[None])
    ST = int(instance.Steps_Number.extract_values()[None])

    Discount_Rate = instance.Discount_Rate.value

    upgrade_years_list = [1 for i in range(ST)]
    s_dur = instance.Step_Duration.value
    for i in range(1, ST): 
        upgrade_years_list[i] = upgrade_years_list[i-1] + s_dur    
    yu_tuples_list = [0 for i in range(1,Y+1)]    
    if ST == 1:    
        for y in range(1,Y+1):            
            yu_tuples_list[y-1] = (y, 1)    
    else:        
        for y in range(1,Y+1):            
            for i in range(len(upgrade_years_list)-1):
                if y >= upgrade_years_list[i] and y < upgrade_years_list[i+1]:
                    yu_tuples_list[y-1] = (y, [st for st in range(ST)][i+1])                
                elif y >= upgrade_years_list[-1]:
                    yu_tuples_list[y-1] = (y, ST)   
    tup_list = [[] for i in range(ST-1)]  
    for i in range(0,ST-1):
        tup_list[i] = yu_tuples_list[s_dur*i + s_dur]      
  
    "Generating years-steps tuples list"
    steps = [i for i in range(1, ST+1)]
    
    years_steps_list = [1 for i in range(1, ST+1)]
    s_dur = instance.Step_Duration.value
    for i in range(1, ST): 
        years_steps_list[i] = years_steps_list[i-1] + s_dur
    ys_tuples_list = [[] for i in range(1, Y+1)]
    for y in range(1, Y+1):  
        if len(years_steps_list) == 1:
            ys_tuples_list[y-1] = (y,1)
        else:
            for i in range(len(years_steps_list)-1):
                if y >= years_steps_list[i] and y < years_steps_list[i+1]:
                    ys_tuples_list[y-1] = (y, steps[i])       
                elif y >= years_steps_list[-1]:
                    ys_tuples_list[y-1] = (y, len(steps)) 
    

    Electric_Demand = pd.DataFrame.from_dict(instance.Energy_Demand.extract_values(), orient='index') #[Wh]
    Electric_Demand.index = pd.MultiIndex.from_tuples(list(Electric_Demand.index))
    Electric_Demand = Electric_Demand.groupby(level=[1], axis=0, sort=False).sum()
    RES_Nominal_Capacity = instance.RES_Nominal_Capacity.extract_values()  
    RES_Units = instance.RES_Units.get_values()  
    RES_Inv_Specific_Cost = instance.RES_Specific_Investment_Cost.extract_values()
    RES_OM_Specific_Cost = instance.RES_Specific_OM_Cost.extract_values()
    BESS_Nominal_Capacity = instance.Battery_Nominal_Capacity.extract_values()    
    BESS_Inv_Specific_Cost = instance.Battery_Specific_Investment_Cost.value
    BESS_OM_Specific_Cost = instance.Battery_Specific_OM_Cost.value
    Generator_Nominal_Capacity = instance.Generator_Nominal_Capacity.get_values()    
    Generator_Inv_Specific_Cost = instance.Generator_Specific_Investment_Cost.extract_values()
    Generator_OM_Specific_Cost = instance.Generator_Specific_OM_Cost.extract_values()
    BESS_Inflow = instance.Battery_Inflow.get_values()    
    BESS_Outflow = instance.Battery_Outflow.get_values()    
    BESS_Unit_Repl_Cost = instance.Unitary_Battery_Replacement_Cost.value
    Generator_Energy_Production = instance.Generator_Energy_Production.get_values()
    Generator_Marginal_Cost = instance.Generator_Marginal_Cost.extract_values()
    Net_Present_Demand = sum(Electric_Demand.iloc[i-1,0]/(1+Discount_Rate)**i for i in range(1,(Y+1)))    #[Wh]

    Investment = round((instance.Investment_Cost.value)/1e3,6)
    Fixed_cost = round((instance.Operation_Maintenance_Cost_Act.value)/1e3,6)
    Variable_cost = round((instance.Total_Scenario_Variable_Cost_Act.get_values()[1] - instance.Operation_Maintenance_Cost_Act.value)/1e3, 6)
    Tot_CO2 = round(instance.Scenario_CO2_emission.get_values()[1]/1e3, 6)
    
    r_size = round(RES_Units[1,1]*RES_Nominal_Capacity[1]/1e3, 6)
   
    Battery_capacity = round(BESS_Nominal_Capacity[1]/1e3, 6)

    Generator_size = round(instance.Generator_Nominal_Capacity.get_values()[1,1]/1e3, 6)
    
    if Optimization_Goal == 'NPC':              
        NPC = round((instance.ObjectiveFuntion.expr())/1e3, 6)
                                    
    elif Optimization_Goal == 'Operation cost':
        NPC = round((instance.Scenario_Net_Present_Cost.get_values()[1]*instance.Scenario_Weight.extract_values()[1])/1e3, 6)

    LCOE = round((NPC/Net_Present_Demand)*1e6, 6)

    sensitivity_results.append([Investment, NPC, LCOE, Fixed_cost, Variable_cost,Tot_CO2, r_size, Battery_capacity, Generator_size])
    
    
    tariff = []
    for (y,st) in ys_tuples_list:
        res_yc = (RES_Units[st,1]*RES_Nominal_Capacity[1]*RES_Inv_Specific_Cost[1]*RES_OM_Specific_Cost[1]/1e3) 
        bess_yc = ( BESS_Nominal_Capacity[st]*BESS_Inv_Specific_Cost*BESS_OM_Specific_Cost/1e3) 
        gen_yc = ( Generator_Nominal_Capacity[st,1]*Generator_Inv_Specific_Cost[1]*Generator_OM_Specific_Cost[1]/1e3) 
        fuel_yc = (sum(Generator_Energy_Production[(1,y,1,t)] for t in range(1,P+1))*Generator_Marginal_Cost[(1,y,1)]/1e3) 
        Battery_cost_in = sum(BESS_Inflow[1,y,t]*BESS_Unit_Repl_Cost for t in range(1,P+1))
        Battery_cost_out = sum(BESS_Outflow[1,y,t]*BESS_Unit_Repl_Cost for t in range(1,P+1))
        Battery_Yearly_cost = (Battery_cost_in + Battery_cost_out)/1e3
        tariff_value = res_yc + bess_yc + gen_yc + fuel_yc + Battery_Yearly_cost + 16.25
        tariff.append(tariff_value)
        
    TARIFF.append(tariff)
   
    return sensitivity_results, TARIFF

    