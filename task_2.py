import gurobipy as gp
from gurobipy import GRB

# Data
warehouses = ['W1', 'W2']
stores = ['S1', 'S2', 'S3']

# Supply (+, warehouse) and demand (-, store)
# 供给 (+, 仓库) 和需求 (-, 商店)
supply_demand = {
    ('W1', 'E'): 80, ('W1', 'F'): 70,
    ('W2', 'E'): 70, ('W2', 'F'): 80,
    ('S1', 'E'): -50, ('S1', 'F'): -40,
    ('S2', 'E'): -60, ('S2', 'F'): -50,
    ('S3', 'E'): -40, ('S3', 'F'): -60
}

# Route Capacity and Fixed Cost
# 路线容量和固定成本
capacity = {
    ('W1','S1'): 150, ('W1','S2'): 200, ('W1','S3'): 150,
    ('W2','S1'): 200, ('W2','S2'): 150, ('W2','S3'): 180
}

fixed_cost = {
    ('W1','S1'): 1000, ('W1','S2'): 800, ('W1','S3'): 900,
    ('W2','S1'): 600, ('W2','S2'): 700, ('W2','S3'): 1100
}

# Unit Transportation Cost (Electronic Equipment, Furniture)
# 单位运输成本 (电子设备, 家具)
trans_cost = {
    ('W1','S1','E'): 8, ('W1','S1','F'): 12,
    ('W1','S2','E'): 5, ('W1','S2','F'): 9,
    ('W1','S3','E'): 7, ('W1','S3','F'): 14,
    ('W2','S1','E'): 4, ('W2','S1','F'): 7,
    ('W2','S2','E'): 6, ('W2','S2','F'): 10,
    ('W2','S3','E'): 9, ('W2','S3','F'): 16
}

# Create a MIP model
model = gp.Model("Distribution_Network")

# Decision Variables
x_E = model.addVars(warehouses, stores, name="x_E", lb=0)  # 电子设备运输量
x_F = model.addVars(warehouses, stores, name="x_F", lb=0)  # 家具运输量
y = model.addVars(warehouses, stores, vtype=GRB.BINARY, name="y")  # 路线开启

# Objective Function: Transportation Cost + Fixed Cost
# 目标函数: 运输成本 + 固定成本
transport_cost = gp.quicksum(trans_cost[i,j,'E'] * x_E[i,j] + 
                              trans_cost[i,j,'F'] * x_F[i,j] 
                              for i in warehouses for j in stores)
fixed_costs = gp.quicksum(fixed_cost[i,j] * y[i,j] for i in warehouses for j in stores)
model.setObjective(transport_cost + fixed_costs, GRB.MINIMIZE)

# Constraint 1: Warehouse supply constraint
# 约束1: 仓库供给约束
for i in warehouses:
    model.addConstr(gp.quicksum(x_E[i,j] for j in stores) <= supply_demand[i,'E'], 
                   f"Supply_E_{i}")
    model.addConstr(gp.quicksum(x_F[i,j] for j in stores) <= supply_demand[i,'F'], 
                   f"Supply_F_{i}")
# Constraint 2: Store demand constraint
# 约束2: 商店需求约束
for j in stores:
    model.addConstr(gp.quicksum(x_E[i,j] for i in warehouses) == -supply_demand[j,'E'], 
                   f"Demand_E_{j}")
    model.addConstr(gp.quicksum(x_F[i,j] for i in warehouses) == -supply_demand[j,'F'], 
                   f"Demand_F_{j}")
# Constraint 3: Capacity Constraint
# 约束3: 容量约束
for i in warehouses:
    for j in stores:
        model.addConstr(x_E[i,j] + x_F[i,j] <= capacity[i,j] * y[i,j], 
                       f"Capacity_{i}_{j}")

# Solve MIP
model.optimize()

# result
if model.status == GRB.OPTIMAL:
    print("\n" + "="*60)
    print("MIP OPTIMAL SOLUTION")
    print("="*60)
    
    print(f"\nTotal Cost: ${model.objVal:,.2f}")
    
    #Calculation of transportation costs
    # 运输成本计算
    trans_cost_val = sum(trans_cost[i,j,'E'] * x_E[i,j].x + 
                         trans_cost[i,j,'F'] * x_F[i,j].x 
                         for i in warehouses for j in stores)
    fixed_cost_val = sum(fixed_cost[i,j] * y[i,j].x for i in warehouses for j in stores)
    
    print(f"  Transportation Cost: ${trans_cost_val:,.2f}")
    print(f"  Fixed Cost: ${fixed_cost_val:,.2f}")
    
    print("\nRoutes Opened (y[i,j] = 1):")
    for i in warehouses:
        for j in stores:
            if y[i,j].x > 0.5:
                print(f"  {i} -> {j}")
    
    print("\nShipping Plan (units):")
    print("-" * 60)
    print(f"{'Route':<12} {'Electronics':>12} {'Furniture':>12} {'Total':>10}")
    print("-" * 60)
    
    for i in warehouses:
        for j in stores:
            if x_E[i,j].x > 0.001 or x_F[i,j].x > 0.001:
                e_amt = x_E[i,j].x
                f_amt = x_F[i,j].x
                total = e_amt + f_amt
                print(f"{i}->{j:<8} {e_amt:12.1f} {f_amt:12.1f} {total:10.1f}")
    
    # Verify Supply and Demand Balance
    # 验证供需平衡
    print("\n" + "="*60)
    print("SUPPLY/DEMAND VERIFICATION")
    print("="*60)
    
    # Total Warehouse Shipment Volume
    # 仓库出货总量
    print("\nWarehouse Outbound:")
    for i in warehouses:
        e_total = sum(x_E[i,j].x for j in stores)
        f_total = sum(x_F[i,j].x for j in stores)
        print(f"  {i}: Electronics={e_total:.1f}/{supply_demand[i,'E']}, "
              f"Furniture={f_total:.1f}/{supply_demand[i,'F']}")
    
    # Total Quantity of Goods Received by the Store
    # 商店收货总量
    print("\nStore Inbound:")
    for j in stores:
        e_total = sum(x_E[i,j].x for i in warehouses)
        f_total = sum(x_F[i,j].x for i in warehouses)
        demand_e = -supply_demand[j,'E']
        demand_f = -supply_demand[j,'F']
        print(f"  {j}: Electronics={e_total:.1f}/{demand_e}, "
              f"Furniture={f_total:.1f}/{demand_f}")
    
    # Calculating LP Relaxation and Integrality Gap
    # 计算LP松弛和整合性差距
    print("\n" + "="*60)
    print("LP RELAXATION & INTEGRALITY GAP")
    print("="*60)

    # Create an LP relaxation model
    # 创建LP松弛模型
    model_lp = gp.Model("Distribution_Network_LP")

    # Same variable but y is continuous [0,1]
    # 相同变量但y是连续的 [0,1]
    x_E_lp = model_lp.addVars(warehouses, stores, name="x_E_lp", lb=0)
    x_F_lp = model_lp.addVars(warehouses, stores, name="x_F_lp", lb=0)
    y_lp = model_lp.addVars(warehouses, stores, name="y_lp", lb=0, ub=1)  # 连续
    
    # Same Objective Function
    transport_cost_lp = gp.quicksum(trans_cost[i,j,'E'] * x_E_lp[i,j] + 
                                      trans_cost[i,j,'F'] * x_F_lp[i,j] 
                                      for i in warehouses for j in stores)
    fixed_costs_lp = gp.quicksum(fixed_cost[i,j] * y_lp[i,j] 
                                   for i in warehouses for j in stores)
    model_lp.setObjective(transport_cost_lp + fixed_costs_lp, GRB.MINIMIZE)
    
    # Same Constraints
    for i in warehouses:
        model_lp.addConstr(gp.quicksum(x_E_lp[i,j] for j in stores) <= supply_demand[i,'E'])
        model_lp.addConstr(gp.quicksum(x_F_lp[i,j] for j in stores) <= supply_demand[i,'F'])
    
    for j in stores:
        model_lp.addConstr(gp.quicksum(x_E_lp[i,j] for i in warehouses) == -supply_demand[j,'E'])
        model_lp.addConstr(gp.quicksum(x_F_lp[i,j] for i in warehouses) == -supply_demand[j,'F'])
    
    for i in warehouses:
        for j in stores:
            model_lp.addConstr(x_E_lp[i,j] + x_F_lp[i,j] <= capacity[i,j] * y_lp[i,j])
    
    # Solving the LP relaxation
    model_lp.optimize()
    
    if model_lp.status == GRB.OPTIMAL:
        lp_obj = model_lp.objVal
        mip_obj = model.objVal
        
        print(f"\nMIP Objective: ${mip_obj:,.2f}")
        print(f"LP Relaxation Objective: ${lp_obj:,.2f}")
        
        gap = (mip_obj - lp_obj) / lp_obj * 100
        print(f"\nIntegrality Gap: {gap:.2f}%")
        print(f"  (MIP is {gap:.2f}% more expensive than LP relaxation)")
        
        print("\nLP Relaxation Route Openings (y values):")
        for i in warehouses:
            for j in stores:
                if y_lp[i,j].x > 0.001:
                    print(f"  {i} -> {j}: {y_lp[i,j].x:.3f}")
    else:
        print("LP relaxation not optimal")
    
else:
    print("No optimal solution found")
