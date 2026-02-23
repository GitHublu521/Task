import gurobipy as gp
from gurobipy import GRB

# 员工数据
employees = [
    "SMITH", "JOHNSON", "WILLIAMS", "JONES", "BROWN", "DAVIS", "MILLER", 
    "WILSON", "MOORE", "TAYLOR", "ANDERSON", "THOMAS", "JACKSON", "WHITE", 
    "HARRIS", "MARTIN", "THOMPSON", "GARCIA", "MARTINEZ", "ROBINSON"
]

# 员工参数 [min_hours, max_hours, wage]
emp_params = {
    "SMITH": [6, 8, 30], "JOHNSON": [6, 8, 50], "WILLIAMS": [6, 8, 30],
    "JONES": [6, 8, 30], "BROWN": [6, 8, 40], "DAVIS": [6, 8, 50],
    "MILLER": [6, 8, 45], "WILSON": [6, 8, 30], "MOORE": [6, 8, 35],
    "TAYLOR": [6, 8, 40], "ANDERSON": [2, 3, 60], "THOMAS": [2, 4, 40],
    "JACKSON": [2, 4, 60], "WHITE": [2, 6, 55], "HARRIS": [2, 6, 45],
    "MARTIN": [2, 3, 40], "THOMPSON": [2, 5, 50], "GARCIA": [2, 4, 50],
    "MARTINEZ": [2, 4, 40], "ROBINSON": [2, 5, 50]
}

# 可用性约束（默认全天可用）
availability = {emp: [1]*24 for emp in employees}

# 特殊约束修正
# SMITH: 6-20点可用
for t in list(range(0, 6)) + list(range(21, 24)):
    availability["SMITH"][t] = 0

# MILLER: 6-18点可用
for t in list(range(0, 6)) + list(range(19, 24)):
    availability["MILLER"][t] = 0

# ANDERSON: 0-6点 和 18-24点可用
for t in list(range(6, 18)):
    availability["ANDERSON"][t] = 0

# JACKSON: 8-16点可用
for t in list(range(0, 8)) + list(range(17, 24)):
    availability["JACKSON"][t] = 0

# THOMPSON: 12-24点可用
for t in list(range(0, 12)):
    availability["THOMPSON"][t] = 0

# 验证可用性设置（可选）
print("Availability check:")
print(f"SMITH (0-5): {availability['SMITH'][0:6]}")
print(f"SMITH (21-23): {availability['SMITH'][21:24]}")
print(f"ANDERSON (6-17): {availability['ANDERSON'][6:18]}")
print(f"JACKSON (0-7): {availability['JACKSON'][0:8]}")
print(f"THOMPSON (0-11): {availability['THOMPSON'][0:12]}")

# 每小时需求（24小时，0-23）
hourly_req = [1, 1, 2, 3, 6, 6, 7, 8, 9, 8, 8, 8, 7, 6, 6, 5, 5, 4, 4, 3, 2, 2, 2, 2]

# 创建模型
model = gp.Model("Employee_Scheduling")
model.setParam('OutputFlag', 1)  # 显示求解过程

# 决策变量
start = model.addVars(employees, range(24), vtype=GRB.BINARY, name="start")
work = model.addVars(employees, range(24), vtype=GRB.BINARY, name="work")

# 目标函数：最小化总工资成本
model.setObjective(
    gp.quicksum(emp_params[emp][2] * work[emp, t] 
                for emp in employees for t in range(24)),
    GRB.MINIMIZE
)

# 约束1: 每个员工最多开始一次工作
for emp in employees:
    model.addConstr(gp.quicksum(start[emp, t] for t in range(24)) <= 1, 
                   f"OneStart_{emp}")

# 约束2: 工作时长限制
for emp in employees:
    total_hours = gp.quicksum(work[emp, t] for t in range(24))
    model.addConstr(total_hours >= emp_params[emp][0], f"MinHours_{emp}")
    model.addConstr(total_hours <= emp_params[emp][1], f"MaxHours_{emp}")

# 约束3: 可用性约束
for emp in employees:
    for t in range(24):
        if availability[emp][t] == 0:
            model.addConstr(work[emp, t] == 0, f"Avail_{emp}_{t}")
            model.addConstr(start[emp, t] == 0, f"StartAvail_{emp}_{t}")

# 约束4: 连续性约束
for emp in employees:
    # 第一个小时
    model.addConstr(work[emp, 0] == start[emp, 0], f"FirstHour_{emp}")
    
    # 后续小时
    for t in range(1, 24):
        # 如果t时刻在工作，那么要么t-1时刻在工作，要么t时刻是开始时间
        model.addConstr(work[emp, t] <= work[emp, t-1] + start[emp, t], 
                       f"Continuity1_{emp}_{t}")
        # 如果t时刻在工作且t-1时刻不在工作，那么t必须是开始时间
        model.addConstr(work[emp, t] >= work[emp, t-1] + start[emp, t] - 1,
                       f"Continuity2_{emp}_{t}")

# 约束5: 每小时人员需求
for t in range(24):
    model.addConstr(gp.quicksum(work[emp, t] for emp in employees) >= hourly_req[t],
                   f"Demand_{t}")

# 求解
model.optimize()

# 输出结果
if model.status == GRB.OPTIMAL:
    print("\n" + "="*80)
    print("OPTIMAL SCHEDULE FOUND")
    print("="*80)
    
    print(f"\nTotal Daily Cost: ${model.objVal:,.2f}")
    
    print("\nEmployee Schedules:")
    print("-" * 80)
    print(f"{'Employee':<12} {'Hours':<8} {'Start-End':<15} {'Wage':<8} {'Cost':<10}")
    print("-" * 80)
    
    total_hours_all = 0
    total_cost = 0
    
    for emp in employees:
        # 找出工作时间
        working_hours = []
        for t in range(24):
            if work[emp, t].x > 0.5:
                working_hours.append(t)
        
        if working_hours:
            start_time = working_hours[0]
            end_time = working_hours[-1] + 1
            hours_worked = len(working_hours)
            wage = emp_params[emp][2]
            cost = hours_worked * wage
            
            print(f"{emp:<12} {hours_worked:<8} {start_time:02d}:00-{end_time:02d}:00  "
                  f"${wage:<7} ${cost:<8.0f}")
            
            total_hours_all += hours_worked
            total_cost += cost
    
    print("-" * 80)
    print(f"{'TOTAL':<12} {total_hours_all:<8} {'':<15} {'':<8} ${total_cost:>8.2f}")
    
    # 验证每小时覆盖
    print("\nHourly Coverage Check:")
    print("-" * 60)
    print(f"{'Hour':<6} {'Required':<10} {'Actual':<10} {'Status':<10}")
    print("-" * 60)
    
    all_good = True
    coverage = []
    for t in range(24):
        actual = sum(work[emp, t].x for emp in employees)
        coverage.append(actual)
        status = "✓" if actual >= hourly_req[t] - 0.1 else "✗"  # 允许浮点误差
        if actual < hourly_req[t] - 0.1:
            all_good = False
        print(f"{t:02d}-{t+1:02d}  {hourly_req[t]:<10} {actual:<10.0f} {status:<10}")
    
    print("-" * 60)
    if all_good:
        print("✓ All hourly requirements satisfied!")
    else:
        print("✗ Some hourly requirements NOT satisfied!")
    
    # 计算利用率
    total_capacity = sum(emp_params[emp][1] for emp in employees)
    utilization = total_hours_all / total_capacity * 100
    
    print(f"\nStatistics:")
    print(f"  Total Capacity: {total_capacity} hours")
    print(f"  Total Scheduled: {total_hours_all} hours")
    print(f"  Utilization: {utilization:.1f}%")
    
    # 找出哪些员工没被安排工作
    not_working = [emp for emp in employees 
                   if all(work[emp, t].x < 0.5 for t in range(24))]
    if not_working:
        print(f"\nEmployees NOT scheduled: {', '.join(not_working)}")
    
    # 绘制需求vs覆盖图（文本版）
    print("\nDemand vs Coverage Visualization:")
    print("Hour: 0    2    4    6    8    10   12   14   16   18   20   22")
    print("Req: ", end="")
    for t in range(24):
        if t % 2 == 0:
            print(f"{hourly_req[t]:2d}  ", end="")
    print("\nCov: ", end="")
    for t in range(24):
        if t % 2 == 0:
            print(f"{int(coverage[t]):2d}  ", end="")
    print()
    
else:
    print("No optimal solution found")
    print(f"Model status: {model.status}")
