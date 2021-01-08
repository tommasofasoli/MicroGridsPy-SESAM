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
import numpy as np
import os
from pandas import ExcelWriter
from win32com.client import Dispatch
import time

import warnings
warnings.filterwarnings("ignore")


#%% Energy balances
def TimeSeries(instance):
    
    nS = int(instance.Scenarios.extract_values()[None])
    nP = int(instance.Periods.extract_values()[None])
    nY = int(instance.Years.extract_values()[None])
    nC = int(instance.Classes.extract_values()[None])

    StartDate = instance.StartDate.extract_values()[None]
    dateInd = pd.DatetimeIndex(start=StartDate, periods=nP, freq='1min')

    "Electricity balance terms"
    EE_Demand      = pd.DataFrame.from_dict(instance.Electric_Energy_Demand.extract_values(), orient='index')
    EE_Lost_Load   = pd.DataFrame.from_dict(instance.Lost_Load_EE.get_values(), orient='index')
    EE_Curtailment = pd.DataFrame.from_dict(instance.Electric_Curtailment.get_values(), orient='index')
    EE_RES         = pd.DataFrame.from_dict(instance.RES_Energy_Production.get_values(), orient='index')
    EE_BESS_Out    = pd.DataFrame.from_dict(instance.BESS_Outflow.get_values(), orient='index')
    EE_BESS_In     = pd.DataFrame.from_dict(instance.BESS_Inflow.get_values(), orient='index')
    EE_Gen_Prod    = pd.DataFrame.from_dict(instance.Generator_Energy_Production.get_values(), orient='index')
    EE_ElRes_Cons  = pd.DataFrame.from_dict(instance.Tot_Electric_Resistance_Energy_Production.get_values(), orient='index')
    # Additional useful terms
    Diesel_Cons    = pd.DataFrame.from_dict(instance.Diesel_Consumption.get_values(), orient='index')
    BESS_SOC       = pd.DataFrame.from_dict(instance.BESS_State_of_Charge.get_values(), orient='index')
    
    "Thermal energy balance terms"
    Th_Demand       = pd.DataFrame.from_dict(instance.Thermal_Energy_Demand.extract_values(), orient='index')
    Th_Lost_Load    = pd.DataFrame.from_dict(instance.Lost_Load_Th.get_values(), orient='index')
    Th_Curtailment  = pd.DataFrame.from_dict(instance.Thermal_Energy_Curtailment.extract_values(), orient='index')
    Th_Boiler_Prod  = pd.DataFrame.from_dict(instance.Boiler_Energy_Production.extract_values(), orient='index')
    Th_Tank_Out     = pd.DataFrame.from_dict(instance.Tank_Outflow.get_values(), orient='index')
    Th_Tank_In      = pd.DataFrame.from_dict(instance.Tank_Inflow.get_values(), orient='index')
    Th_ElRes_Prod   = pd.DataFrame.from_dict(instance.Electric_Resistance_Energy_Production.get_values(), orient='index')
    Th_SC_Prod      = pd.DataFrame.from_dict(instance.SC_Energy_Production.get_values(), orient='index')
    # Additional useful terms
    NG_Cons         = pd.DataFrame.from_dict(instance.NG_Consumption.get_values(), orient='index')
    Tank_SOC        = pd.DataFrame.from_dict(instance.Tank_State_of_Charge.get_values(), orient='index')

    "Preparing for export"
    EE_TimeSeries = {}
    Th_TimeSeries = {}
    
    for s in range(nS):
       EE_TimeSeries[s] = pd.concat([EE_Demand.iloc[s*nP:(s*nP+nP),:], EE_Lost_Load.iloc[s*nP:(s*nP+nP),:], EE_Curtailment.iloc[s*nP:(s*nP+nP),:], EE_ElRes_Cons.iloc[s*nP:(s*nP+nP),:],  EE_RES.iloc[s*nP:(s*nP+nP),:],  EE_BESS_Out.iloc[s*nP:(s*nP+nP),:], EE_BESS_In.iloc[s*nP:(s*nP+nP),:], EE_Gen_Prod.iloc[s*nP:(s*nP+nP),:], Diesel_Cons.iloc[s*nP:(s*nP+nP),:], BESS_SOC.iloc[s*nP:(s*nP+nP),:]], axis=1)
       EE_TimeSeries[s].columns = ['Demand','Lost Load', 'Curtailment', 'Electric resistance consumption', 'RES production', 'BESS outflow', 'BESS inflow', 'Genset production', 'Diesel consumption', 'BESS state of charge']
       EE_TimeSeries[s].index = dateInd
       EE_TimeSeries['Sc'+str(s+1)] = EE_TimeSeries.pop(s)
       EE_path = 'Results/TimeSeries/Sc'+str(s+1)
       if not os.path.exists(EE_path):
           os.makedirs(EE_path)
       EE_TimeSeries['Sc'+str(s+1)].to_csv(EE_path+'/EE_TimeSeries.csv')
       
       Th_TimeSeries[s] = {}
       
       for c in range(nC):
           Th_TimeSeries[s][c] = pd.concat([Th_Demand.iloc[(s*c*nP+c*nP):(s*c*nP+c*nP+nP),:], Th_Lost_Load.iloc[(s*c*nP+c*nP):(s*c*nP+c*nP+nP),:], Th_SC_Prod.iloc[(s*c*nP+c*nP):(s*c*nP+c*nP+nP),:],  Th_Tank_Out.iloc[(s*c*nP+c*nP):(s*c*nP+c*nP+nP),:], Th_Tank_In.iloc[(s*c*nP+c*nP):(s*c*nP+c*nP+nP),:], Th_Boiler_Prod.iloc[(s*c*nP+c*nP):(s*c*nP+c*nP+nP),:], Th_ElRes_Prod.iloc[(s*c*nP+c*nP):(s*c*nP+c*nP+nP),:], Th_Curtailment.iloc[(s*c*nP+c*nP):(s*c*nP+c*nP+nP),:], NG_Cons.iloc[(s*c*nP+c*nP):(s*c*nP+c*nP+nP),:], Tank_SOC.iloc[(s*c*nP+c*nP):(s*c*nP+c*nP+nP),:]], axis=1)
           Th_TimeSeries[s][c].columns = ['Demand','Lost Load', 'SC production', 'Tank outflow', 'Tank inflow', 'Boiler production', 'Electric resistance production', 'Curtailment', 'NG consumption', 'Tank state of charge']
           Th_TimeSeries[s][c].index = dateInd
           Th_TimeSeries[s]['Class'+str(c+1)] = Th_TimeSeries[s].pop(c)
           
       Th_TimeSeries['Sc'+str(s+1)] = Th_TimeSeries.pop(s)
   
       for c in range(nC):
           Th_path = 'Results/TimeSeries/Sc'+str(s+1)
           if not os.path.exists(EE_path):
               os.makedirs(EE_path)
           Th_TimeSeries['Sc'+str(s+1)]['Class'+str(c+1)].to_csv(Th_path+'/Th_TimeSeries_Class'+str(c+1)+'.csv')
                                                                  
    TimeSeries = {'EE': EE_TimeSeries,
                  'Th': Th_TimeSeries}
    
    return(TimeSeries)


#%% Energy System Configuration
def EnergySystemInfo(instance):
    
    "System size"
    nS = int(instance.Scenarios.extract_values()[None])
    nP = int(instance.Periods.extract_values()[None])
    nY = int(instance.Years.extract_values()[None])
    nC = int(instance.Classes.extract_values()[None])
    dr = instance.Discount_Rate.extract_values()[None]

    # Electricity system components
    RES_Capacity = pd.DataFrame(['RES', 'kW', instance.RES_Units.get_values()[None]*instance.RES_Nominal_Capacity.extract_values()[None]]).T.set_index([0,1])
    BESS_Capacity = pd.DataFrame(['Battery Storage System', 'kW', instance.BESS_Nominal_Capacity.get_values()[None]]).T.set_index([0,1])
    Gen_Capacity = pd.DataFrame(['Genset', 'kW', instance.Generator_Nominal_Capacity.get_values()[None]]).T.set_index([0,1])
    
    EE_system = pd.concat([RES_Capacity,BESS_Capacity,Gen_Capacity], axis=0)
    EE_system.index.names = ['Component', 'Unit']
    EE_system.columns = ['Total']

    # Thermal system components
    SC_Capacity = [instance.SC_Units.get_values()[i]*instance.SC_Nominal_Capacity.extract_values()[None] for i in instance.SC_Units.get_values().keys()]
    SC_Capacity = [i for i in SC_Capacity]
    SC_Capacity = pd.DataFrame([['Solar collector', 'kW'] + SC_Capacity]).set_index([0,1])

    Boiler_Capacity = list(instance.Boiler_Nominal_Capacity.get_values().values())
    Boiler_Capacity = [i for i in Boiler_Capacity]
    Boiler_Capacity = pd.DataFrame([['NG Boiler', 'kW'] + Boiler_Capacity]).set_index([0,1])

    Tank_Capacity = list(instance.Tank_Nominal_Capacity.get_values().values())
    Tank_Capacity = [i for i in Tank_Capacity]
    Tank_Capacity = pd.DataFrame([['Tank', 'kW'] + Tank_Capacity]).set_index([0,1])

    ElRes_Power = list(instance.Electric_Resistance_Nominal_Power.get_values().values())
    ElRes_Power = [i for i in ElRes_Power]
    ElRes_Power = pd.DataFrame([['Electric resistance', 'kW'] + ElRes_Power]).set_index([0,1])
    
    Th_system = pd.concat([SC_Capacity,Tank_Capacity,Boiler_Capacity,ElRes_Power], axis=0)
    Th_system = pd.concat([Th_system, Th_system.sum(1).to_frame()],axis=1)
    Th_system.index.names = ['Th Components', 'Unit']
    Th_system.columns = ['Class'+str(c+1) for c in range(nC)]+['Total']
    
    EnergySystemSize = pd.concat([EE_system, Th_system],axis=0).fillna("-")
    
    
    #%% Economic Analysis
    "Net Present Cost"
    NPC = pd.DataFrame(['Net Present Cost', 'System', '-', 'MUSD', instance.ObjectiveFuntion.expr()/1e6]).T.set_index([0,1,2,3])
    NPC.columns = ['Total']
    NPC.index.names = ['Cost item', 'Component', 'Scenario', 'Unit']
    
    "Investment Cost"   
    RES_Investment_Cost = instance.RES_Investment_Cost.extract_values()[None]
    RES_Investment_Cost = pd.DataFrame(['Investment Cost', 'RES', '-', 'MUSD', RES_Investment_Cost/1e6]).T.set_index([0,1,2,3])
    RES_Investment_Cost.columns = ['Total']

    BESS_Investment_Cost = instance.BESS_Investment_Cost.extract_values()[None]
    BESS_Investment_Cost = pd.DataFrame(['Investment Cost', 'Battery Storage System', '-', 'MUSD', BESS_Investment_Cost/1e6]).T.set_index([0,1,2,3])
    BESS_Investment_Cost.columns = ['Total']

    Gen_Investment_Cost = instance.Generator_Investment_Cost.extract_values()[None]
    Gen_Investment_Cost = pd.DataFrame(['Investment Cost', 'Genset', '-', 'MUSD', Gen_Investment_Cost/1e6]).T.set_index([0,1,2,3])
    Gen_Investment_Cost.columns = ['Total']

    SC_Investment_Cost = pd.DataFrame.from_dict(instance.SC_Investment_Cost.get_values(), orient='index').T
    SC_Investment_Cost = pd.concat([SC_Investment_Cost/1e6, pd.DataFrame([SC_Investment_Cost.sum(1).values[0]/1e6])], axis=1)
    SC_Investment_Cost.columns = ['Class'+str(c+1) for c in range(nC)]+['Total']
    SC_Investment_Cost = pd.concat([pd.DataFrame(['Investment Cost', 'Solar collector', '-', 'MUSD']).T, SC_Investment_Cost], axis=1).set_index([0,1,2,3])

    Boiler_Investment_Cost = pd.DataFrame.from_dict(instance.Boiler_Investment_Cost.get_values(), orient='index').T
    Boiler_Investment_Cost = pd.concat([Boiler_Investment_Cost/1e6, pd.DataFrame([Boiler_Investment_Cost.sum(1).values[0]/1e6])], axis=1)
    Boiler_Investment_Cost.columns = ['Class'+str(c+1) for c in range(nC)]+['Total']
    Boiler_Investment_Cost = pd.concat([pd.DataFrame(['Investment Cost', 'NG Boiler', '-', 'MUSD']).T, Boiler_Investment_Cost], axis=1).set_index([0,1,2,3])

    Tank_Investment_Cost = pd.DataFrame.from_dict(instance.Tank_Investment_Cost.get_values(), orient='index').T
    Tank_Investment_Cost = pd.concat([Tank_Investment_Cost/1e6, pd.DataFrame([Tank_Investment_Cost.sum(1).values[0]/1e6])], axis=1)
    Tank_Investment_Cost.columns = ['Class'+str(c+1) for c in range(nC)]+['Total']
    Tank_Investment_Cost = pd.concat([pd.DataFrame(['Investment Cost', 'Tank', '-', 'MUSD']).T, Tank_Investment_Cost], axis=1).set_index([0,1,2,3])

    ElRes_Investment_Cost = pd.DataFrame.from_dict(instance.Electric_Resistance_Investment_Cost.get_values(), orient='index').T
    ElRes_Investment_Cost = pd.concat([ElRes_Investment_Cost/1e6, pd.DataFrame([ElRes_Investment_Cost.sum(1).values[0]/1e6])], axis=1)
    ElRes_Investment_Cost.columns = ['Class'+str(c+1) for c in range(nC)]+['Total']
    ElRes_Investment_Cost = pd.concat([pd.DataFrame(['Investment Cost', 'Electric resistance', '-', 'MUSD']).T, ElRes_Investment_Cost], axis=1).set_index([0,1,2,3])

    BESS_Replacement_Cost = instance.BESS_Replacement_Cost.extract_values()[None]
    BESS_Replacement_Cost = pd.DataFrame(['Replacement Cost', 'Battery Storage System', '-', 'MUSD', BESS_Replacement_Cost/1e6]).T.set_index([0,1,2,3])
    BESS_Replacement_Cost.columns = ['Total']

    
    "Fixed Costs"   
    RES_OM_Cost = instance.RES_OM_Cost.extract_values()[None]
    RES_OM_Cost = pd.DataFrame(['Fixed Cost', 'RES', '-', 'MUSD', RES_OM_Cost/1e6]).T.set_index([0,1,2,3])
    RES_OM_Cost.columns = ['Total']

    BESS_OM_Cost = instance.BESS_OM_Cost.extract_values()[None]
    BESS_OM_Cost = pd.DataFrame(['Fixed Cost', 'Battery Storage System', '-', 'MUSD', BESS_OM_Cost/1e6]).T.set_index([0,1,2,3])
    BESS_OM_Cost.columns = ['Total']

    Generator_OM_Cost = instance.Generator_OM_Cost.extract_values()[None]
    Generator_OM_Cost = pd.DataFrame(['Fixed Cost', 'Genset', '-', 'MUSD', Generator_OM_Cost/1e6]).T.set_index([0,1,2,3])
    Generator_OM_Cost.columns = ['Total']

    SC_OM_Cost = pd.DataFrame.from_dict(instance.SC_OM_Cost.get_values(), orient='index').T
    SC_OM_Cost = pd.concat([SC_OM_Cost/1e6, pd.DataFrame([SC_OM_Cost.sum(1).values[0]/1e6])], axis=1)
    SC_OM_Cost.columns = ['Class'+str(c+1) for c in range(nC)]+['Total']
    SC_OM_Cost = pd.concat([pd.DataFrame(['Fixed Cost', 'Solar collector', '-', 'MUSD']).T, SC_OM_Cost], axis=1).set_index([0,1,2,3])
    
    Boiler_OM_Cost = pd.DataFrame.from_dict(instance.Boiler_OM_Cost.get_values(), orient='index').T
    Boiler_OM_Cost = pd.concat([Boiler_OM_Cost/1e6, pd.DataFrame([Boiler_OM_Cost.sum(1).values[0]/1e6])], axis=1)
    Boiler_OM_Cost.columns = ['Class'+str(c+1) for c in range(nC)]+['Total']
    Boiler_OM_Cost = pd.concat([pd.DataFrame(['Fixed Cost', 'NG Boiler', '-', 'MUSD']).T, Boiler_OM_Cost], axis=1).set_index([0,1,2,3])

    Tank_OM_Cost = pd.DataFrame.from_dict(instance.Tank_OM_Cost.get_values(), orient='index').T
    Tank_OM_Cost = pd.concat([Tank_OM_Cost/1e6, pd.DataFrame([Tank_OM_Cost.sum(1).values[0]/1e6])], axis=1)
    Tank_OM_Cost.columns = ['Class'+str(c+1) for c in range(nC)]+['Total']
    Tank_OM_Cost = pd.concat([pd.DataFrame(['Fixed Cost', 'Tank', '-', 'MUSD']).T, Tank_OM_Cost], axis=1).set_index([0,1,2,3])

    ElRes_OM_Cost = pd.DataFrame.from_dict(instance.Electric_Resistance_OM_Cost.get_values(), orient='index').T
    ElRes_OM_Cost = pd.concat([ElRes_OM_Cost/1e6, pd.DataFrame([ElRes_OM_Cost.sum(1).values[0]/1e6])], axis=1)
    ElRes_OM_Cost.columns = ['Class'+str(c+1) for c in range(nC)]+['Total']
    ElRes_OM_Cost = pd.concat([pd.DataFrame(['Fixed Cost', 'Electric resistance', '-', 'MUSD']).T, ElRes_OM_Cost], axis=1).set_index([0,1,2,3])


    "Variable costs"
    Total_Diesel_Cost = pd.DataFrame()
    Total_Diesel_Cost_index = [['Fuel cost' for s in range(1,nS+1)], ['Genset' for s in range(1,nS+1)], [str(s) for s in range(1,nS+1)], ['MUSD' for s in range(1,nS+1)]]
    Total_NG_Cost = pd.DataFrame()
    Total_NG_Cost_index = [['Fuel cost' for s in range(1,nS+1)], ['Boiler' for s in range(1,nS+1)], [str(s) for s in range(1,nS+1)], ['MUSD' for s in range(1,nS+1)]]    
    
    EE_LL_Cost = pd.DataFrame()
    EE_LL_Cost_index = [['Electric lost load cost' for s in range(1,nS+1)], ['System' for s in range(1,nS+1)], [str(s) for s in range(1,nS+1)], ['MUSD' for s in range(1,nS+1)]]
    Th_LL_Cost = pd.DataFrame()
    Th_LL_Cost_index = [['Thermal lost load cost' for s in range(1,nS+1)], ['System' for s in range(1,nS+1)], [str(s) for s in range(1,nS+1)], ['MUSD' for s in range(1,nS+1)]]
    
    for s in range(1,nS+1):
        Total_Diesel_Cost = pd.concat([Total_Diesel_Cost, pd.DataFrame([instance.Total_Diesel_Cost.extract_values()[s]/1e6])], axis=0)
        EE_LL_Cost = pd.concat([EE_LL_Cost, pd.DataFrame([instance.Scenario_Lost_Load_Cost_EE.extract_values()[s]/1e6])], axis=0)
        
        for c in range(1,nC+1):
            Total_NG_Cost = pd.concat([Total_NG_Cost, pd.DataFrame([instance.Total_NG_Cost.get_values()[(s,c)]/1e6])], axis=1)
            Th_LL_Cost = pd.concat([Th_LL_Cost, pd.DataFrame([instance.Scenario_Lost_Load_Cost_Th.get_values()[(s,c)]/1e6])], axis=1)
            
        Total_NG_Cost = pd.concat([Total_NG_Cost, pd.DataFrame([Total_NG_Cost.sum(1).values[0]])], axis=1)
        Total_NG_Cost.columns = ['Class'+str(c+1) for c in range(nC)]+['Total']

        Th_LL_Cost = pd.concat([Th_LL_Cost, pd.DataFrame([Th_LL_Cost.sum(1).values[0]])], axis=1)
        Th_LL_Cost.columns = ['Class'+str(c+1) for c in range(nC)]+['Total']
    
    Total_Diesel_Cost.index = pd.MultiIndex.from_arrays(Total_Diesel_Cost_index)
    Total_Diesel_Cost.columns = ['Total']
    Total_NG_Cost.index = pd.MultiIndex.from_arrays(Total_NG_Cost_index)
    EE_LL_Cost.index = pd.MultiIndex.from_arrays(EE_LL_Cost_index)
    EE_LL_Cost.columns = ['Total']
    Th_LL_Cost.index = pd.MultiIndex.from_arrays(Th_LL_Cost_index)
    
  
    "Concatenating"
    EE_Inv_Cost = pd.concat([RES_Investment_Cost,BESS_Investment_Cost,Gen_Investment_Cost], axis=0)
    EE_Inv_Cost.index.names = NPC.index.names
    
    Th_Inv_Cost = pd.concat([SC_Investment_Cost,Boiler_Investment_Cost,Tank_Investment_Cost,ElRes_Investment_Cost], axis=0)
    Th_Inv_Cost.index.names = NPC.index.names

    EE_OM_Cost = pd.concat([RES_OM_Cost,BESS_OM_Cost,Generator_OM_Cost], axis=0)
    EE_OM_Cost.index.names = NPC.index.names
    
    Th_OM_Cost = pd.concat([SC_OM_Cost,Boiler_OM_Cost,Tank_OM_Cost,ElRes_OM_Cost], axis=0)
    Th_OM_Cost.index.names = NPC.index.names

    EnergySystemFixedCost = pd.concat([NPC, EE_Inv_Cost, Th_Inv_Cost, EE_OM_Cost, Th_OM_Cost],axis=0).fillna("-")
    EnergySystemVarCost = pd.concat([BESS_Replacement_Cost, Total_Diesel_Cost, Total_NG_Cost, EE_LL_Cost, Th_LL_Cost], axis=0).fillna("-")
    EnergySystemCost = pd.concat([EnergySystemFixedCost, EnergySystemVarCost], axis=0)


    #%%
    "Energy Indicators"
    
    "TPES [MWh]"
    EE_RES_Prod = pd.DataFrame.from_dict(instance.RES_Energy_Production.get_values(), orient='index').sum(0).to_frame()/1e3/60
    EE_Gen_Prod = pd.DataFrame.from_dict(instance.Generator_Energy_Production.get_values(), orient='index').sum(0).to_frame()/1e3/60
    Th_SC_Prod  = pd.DataFrame.from_dict(instance.SC_Energy_Production.extract_values(), orient='index').sum(0).to_frame()/1e3/60
    Th_Boiler_Prod = pd.DataFrame.from_dict(instance.Boiler_Energy_Production.extract_values(), orient='index').sum(0).to_frame()/1e3/60
    Th_ElRes_Prod  = pd.DataFrame.from_dict(instance.Tot_Electric_Resistance_Energy_Production.get_values(), orient='index').sum(0).to_frame()/1e3/60
    
    eta_Generator = instance.Generator_Efficiency.extract_values()[None]
    eta_Boiler = instance.Boiler_Efficiency.extract_values()[None]
    eta_ElRes = instance.Electric_Resistance_Efficiency.extract_values()[None]
    
    TPES_EE = EE_RES_Prod + EE_Gen_Prod/eta_Generator - Th_ElRes_Prod
    TPES_Th = Th_SC_Prod + Th_Boiler_Prod/eta_Boiler + Th_ElRes_Prod/eta_ElRes
    TPES_tot = TPES_EE + TPES_Th
    TPES_ff  = (EE_Gen_Prod/eta_Generator + Th_Boiler_Prod/eta_Boiler)/TPES_tot
    TPES_res = (EE_RES_Prod + Th_SC_Prod)/TPES_tot
    
    TPES_ind   = ['Total Primary Energy Supply', 'Fossil Primary Energy Supply', 'Renewable Primary Energy Supply']
    TPES_unit  = ['MWh', '%', '%']
    
    TPES = pd.concat([TPES_tot, TPES_ff, TPES_res], axis=0)
    TPES.index = np.arange(0,TPES.shape[0])
    TPES = pd.concat([TPES, TPES_EE, TPES_Th], axis=1).fillna('-')
    TPES.index = pd.MultiIndex.from_arrays([TPES_ind, TPES_unit])
    TPES.columns = ['Total', 'Electric', 'Thermal']
    
    "LCOE [USD/kWh]"
    EE_Demand = pd.DataFrame.from_dict(instance.Electric_Energy_Demand.extract_values(), orient='index').sum(0).to_frame()/1e3/60   #[MWh]
    Th_Demand = pd.DataFrame.from_dict(instance.Thermal_Energy_Demand.extract_values(), orient='index').sum(0).to_frame()/1e3/60    #[MWh]
    Net_Present_Demand = sum((EE_Demand+Th_Demand)/(1+dr)**i for i in range(1,(nY+1)))    #[MWh]
    LCOE = pd.DataFrame([NPC.iloc[0,0]/Net_Present_Demand.iloc[0,0]*1e3])    #[USD/kWh]
    LCOE.index = pd.MultiIndex.from_arrays([['Levelized Cost of Energy '],['USD/kWh']])
    LCOE.columns = ['Total'] 
    
    "System efficiency"
    eta_EE = EE_Demand/TPES_EE
    eta_Th = Th_Demand/TPES_Th
    eta_tot = (EE_Demand + Th_Demand)/TPES_tot
    
    efficiencies = pd.concat([eta_tot, eta_EE, eta_Th], axis=1)
    efficiencies.index = pd.MultiIndex.from_arrays([['Efficiency'],['%']])
    efficiencies.columns = TPES.columns
    
    EnergyIndicators = pd.concat([TPES, efficiencies, LCOE], axis=0).fillna('-')
    
    
    "Export"
    ESs_path = 'Results'
    if not os.path.exists(ESs_path):
        os.makedirs(ESs_path)
    
    ESsFile = ExcelWriter(ESs_path+'/EnergySystemSize.xlsx')
    EnergySystemSize.to_excel(ESsFile, sheet_name='Size')   
    EnergySystemCost.to_excel(ESsFile, sheet_name='Cost')  
    EnergyIndicators.to_excel(ESsFile, sheet_name='Indicators')
    
    ESsFile.save()
    
    excel = Dispatch('Excel.Application')   
    cwd = os.getcwd()
    ESsFile = excel.Workbooks.Open(cwd+'/'+ESs_path+'/EnergySystemSize.xlsx')
    for y in range(1,4):
        excel.Worksheets(y).Activate()
        excel.ActiveSheet.Columns.AutoFit()
    ESsFile.Save()
    ESsFile.Close()


    return(EnergySystemSize, EnergySystemCost, EnergyIndicators)



    

