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


from pyomo.opt import SolverFactory
from pyomo.environ import Objective, minimize, Constraint


from Constraints import Net_Present_Cost,Scenario_Net_Present_Cost,Total_Investment_Cost,Generator_Investment_Cost,\
    Boiler_Investment_Cost,Fixed_Costs,Generator_OM_Cost,Boiler_OM_Cost,Variable_Costs,Scenario_Lost_Load_Cost_EE,Total_Diesel_Cost,\
    Scenario_Lost_Load_Cost_Th,Total_NG_Cost,Electric_Energy_Balance,Maximum_Generator_Energy,Diesel_Consumption,Maximum_Lost_Load_EE,\
    Thermal_Energy_Balance,Maximum_Boiler_Energy,NG_Consumption,Maximum_Lost_Load_Th,RES_Investment_Cost,BESS_Investment_Cost,\
    RES_OM_Cost,BESS_OM_Cost,BESS_Replacement_Cost,RES_Energy_Production,BESS_State_of_Charge,Maximum_BESS_Charge,Minimum_BESS_Charge,\
    Max_Power_BESS_Charge,Max_Power_BESS_Discharge,Max_BESS_Inflow,Min_BESS_Outflow,Electric_Resistance_Investment_Cost,Electric_Resistance_OM_Cost,\
    SC_Investment_Cost,SC_OM_Cost,SC_Energy_Production,Tank_State_of_Charge,Maximum_Tank_Charge,Minimum_Tank_Charge,Tank_Investment_Cost,Tank_OM_Cost,\
    Max_Power_Tank_Discharge,Min_Tank_Outflow,Maximum_Electric_Resistance_Energy,Electric_Resistance_Energy_Production,Tot_Electric_Resistance_Energy_Production
        

def Model_Resolution(model,datapath="Inputs/data.dat"):   
    
    "Objective function"
    model.ObjectiveFuntion = Objective(rule=Net_Present_Cost, sense=minimize)  
    
    "Economic constraints"
    model.ScenarioNetPresentCost = Constraint(model.scenario, rule=Scenario_Net_Present_Cost)    
    
    model.TotalInvestmentCost = Constraint(rule=Total_Investment_Cost)
    model.RESInvestmentCost = Constraint(rule=RES_Investment_Cost)
    model.SCInvestmentCost = Constraint(model.classes, rule=SC_Investment_Cost)    
    model.BESSInvestmentCost = Constraint(rule=BESS_Investment_Cost)
    model.GeneratorInvestmentCost = Constraint(rule=Generator_Investment_Cost)
    model.BoilerInvestmentCost = Constraint(model.classes, rule=Boiler_Investment_Cost)
    model.TankInvestmentCost = Constraint(model.classes, rule=Tank_Investment_Cost)    
    model.ElectricResistanceInvestment_Cost = Constraint(model.classes, rule=Electric_Resistance_Investment_Cost)
    
    model.FixedCosts = Constraint(rule=Fixed_Costs)
    model.RESOMCost = Constraint(rule=RES_OM_Cost)
    model.SCOMCost = Constraint(model.classes, rule=SC_OM_Cost)        
    model.BESSOMCost = Constraint(rule=BESS_OM_Cost)
    model.BESSReplacementCost = Constraint(rule=BESS_Replacement_Cost)
    model.GeneratorOMCost = Constraint(rule=Generator_OM_Cost)
    model.BoilerOMCost = Constraint(model.classes, rule=Boiler_OM_Cost)
    model.TankOMCost = Constraint(model.classes, rule=Tank_OM_Cost)   
    model.ElectricResistanceOMCost = Constraint(model.classes, rule=Electric_Resistance_OM_Cost)
    
    model.VariableCosts = Constraint(model.scenario, rule=Variable_Costs)    
    model.ScenarioLostLoadCostEE = Constraint(model.scenario, rule=Scenario_Lost_Load_Cost_EE)    
    model.TotalDieselCost = Constraint(model.scenario, rule=Total_Diesel_Cost)    
    model.ScenarioLostLoadCostTh = Constraint(model.scenario,model.classes, rule=Scenario_Lost_Load_Cost_Th)    
    model.TotalNGCost = Constraint(model.scenario,model.classes, rule=Total_NG_Cost)    
    
    "Electricity generation system constraints" 
    model.ElectricEnergyBalance = Constraint(model.scenario,model.periods, rule=Electric_Energy_Balance)    
    
    model.RESEnergyProduction = Constraint(model.scenario,model.periods, rule=RES_Energy_Production)    
    
    model.BESSStateOfCharge = Constraint(model.scenario,model.periods, rule=BESS_State_of_Charge)    
    model.MaximumBESSCharge = Constraint(model.scenario,model.periods, rule=Maximum_BESS_Charge)    
    model.MinimumBESSCharge = Constraint(model.scenario,model.periods, rule=Minimum_BESS_Charge)    
    model.MaxPowerBESSCharge = Constraint(rule=Max_Power_BESS_Charge)    
    model.MaxPowerBESSDischarge = Constraint(rule=Max_Power_BESS_Discharge)    
    model.MaxBESSInflow = Constraint(model.scenario,model.periods, rule=Max_BESS_Inflow)    
    model.Min_BESS_Outflow = Constraint(model.scenario,model.periods, rule=Min_BESS_Outflow)    

    model.MaximumGeneratorEnergy = Constraint(model.scenario,model.periods, rule=Maximum_Generator_Energy)    
    model.DieselConsumption = Constraint(model.scenario,model.periods, rule=Diesel_Consumption)    
    model.MaximumLostLoadEE = Constraint(model.scenario, rule=Maximum_Lost_Load_EE)    

    "Thermal energy generation system constraints" 
    model.ThermalEnergyBalance = Constraint(model.scenario,model.classes,model.periods, rule=Thermal_Energy_Balance)    
    model.MaximumBoilerEnergy = Constraint(model.scenario,model.classes,model.periods, rule=Maximum_Boiler_Energy)    

    model.SCEnergyProduction = Constraint(model.scenario,model.classes,model.periods, rule=SC_Energy_Production)   

    model.TankStateOfCharge = Constraint(model.scenario,model.classes,model.periods, rule=Tank_State_of_Charge)    
    model.MaximumTankCharge = Constraint(model.scenario,model.classes,model.periods, rule=Maximum_Tank_Charge)    
    model.MinimumTankCharge = Constraint(model.scenario,model.classes,model.periods, rule=Minimum_Tank_Charge)    
    model.MaxPowerTankDischarge = Constraint(model.classes, rule=Max_Power_Tank_Discharge)    
    model.Min_Tank_Outflow = Constraint(model.scenario,model.classes,model.periods, rule=Min_Tank_Outflow)    

    model.MaximumElectricResistanceEnergy = Constraint(model.scenario,model.classes,model.periods, rule=Maximum_Electric_Resistance_Energy)    
    model.ElectricResistanceEnergyProduction = Constraint(model.scenario,model.classes,model.periods, rule=Electric_Resistance_Energy_Production)           
    model.TotElectricResistanceEnergyProduction = Constraint(model.scenario,model.periods, rule=Tot_Electric_Resistance_Energy_Production)           

    model.NGConsumption = Constraint(model.scenario,model.classes,model.periods, rule=NG_Consumption)    
    model.MaximumLostLoadTh = Constraint(model.scenario,model.classes, rule=Maximum_Lost_Load_Th)    
    
    print('Model_Resolution: Constraints imported')
    
    "Load parameters"
    instance = model.create_instance(datapath)
    print('Model_Resolution: Instance created')
    
    "Solver use during the optimization"
    opt = SolverFactory('gurobi')    
    opt.set_options('Method=2 Crossover=0 BarConvTol=1e-4 OptimalityTol=1e-4 FeasibilityTol=1e-4 IterationLimit=1000')
    print('Model_Resolution: Solver called')
    
    "Solving a model instance"
    results = opt.solve(instance, tee=True) 
    print('Model_Resolution: instance solved')

    "Loading solution into instance"
    instance.solutions.load_from(results)
    
    return instance

    