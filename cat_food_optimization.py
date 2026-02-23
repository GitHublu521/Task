# Import Gurobi library
import gurobipy as gp
from gurobipy import GRB

# ===================== 1. Define Data =====================
# Ingredient names
ingredients = ["Chicken", "Beef", "Mutton", "Rice", "Wheat Bran", "Gel"]

# Cost per gram of each ingredient ($/g)
cost = {
    "Chicken": 0.013,
    "Beef": 0.008,
    "Mutton": 0.010,
    "Rice": 0.002,
    "Wheat Bran": 0.005,
    "Gel": 0.001
}

# Nutritional content per gram of each ingredient
nutrition = {
    "Chicken":   {"Protein": 0.100, "Fat": 0.080, "Fibre": 0.001, "Salt": 0.002},
    "Beef":      {"Protein": 0.200, "Fat": 0.100, "Fibre": 0.005, "Salt": 0.005},
    "Mutton":    {"Protein": 0.150, "Fat": 0.110, "Fibre": 0.003, "Salt": 0.007},
    "Rice":      {"Protein": 0.000, "Fat": 0.010, "Fibre": 0.100, "Salt": 0.002},
    "Wheat Bran":{"Protein": 0.040, "Fat": 0.010, "Fibre": 0.150, "Salt": 0.008},
    "Gel":       {"Protein": 0.000, "Fat": 0.000, "Fibre": 0.000, "Salt": 0.000}
}

# Nutritional requirements per can (100g)
min_nutrition = {"Protein": 8.0, "Fat": 6.0}
max_nutrition = {"Fibre": 2.0, "Salt": 0.4}

# ===================== 2. Create Model =====================
model = gp.Model("CatFoodBlending")

# Decision variables: amount of each ingredient used (grams)
x = model.addVars(ingredients, name="x", lb=0)

# ===================== 3. Set Objective Function: Minimize Total Cost =====================
# Total cost = sum of (amount of each ingredient × cost per gram)
model.setObjective(gp.quicksum(x[i] * cost[i] for i in ingredients), GRB.MINIMIZE)

# ===================== 4. Add Constraints =====================
# 1. Total weight constraint: exactly 100g per can
model.addConstr(gp.quicksum(x[i] for i in ingredients) == 100, name="TotalWeight")

# 2. Nutritional constraints
# Protein ≥ 8.0g
model.addConstr(gp.quicksum(x[i] * nutrition[i]["Protein"] for i in ingredients) >= min_nutrition["Protein"], name="ProteinRequirement")

# Fat ≥ 6.0g
model.addConstr(gp.quicksum(x[i] * nutrition[i]["Fat"] for i in ingredients) >= min_nutrition["Fat"], name="FatRequirement")

# Fibre ≤ 2.0g
model.addConstr(gp.quicksum(x[i] * nutrition[i]["Fibre"] for i in ingredients) <= max_nutrition["Fibre"], name="FibreLimit")

# Salt ≤ 0.4g
model.addConstr(gp.quicksum(x[i] * nutrition[i]["Salt"] for i in ingredients) <= max_nutrition["Salt"], name="SaltLimit")

# ===================== 5. Solve the Model =====================
model.optimize()

# ===================== 6. Output Results =====================
if model.status == GRB.OPTIMAL:
    print("\n===== Optimal Formula and Cost =====")
    print(f"Minimum cost per can: ${model.objVal:.4f}")
    print("\nIngredient quantities (g):")
    for i in ingredients:
        if x[i].X > 1e-6:  # Only print ingredients with non-zero quantity
            print(f"{i}: {x[i].X:.2f} g")

    # Bonus: Shadow price of protein constraint
    protein_constr = model.getConstrByName("ProteinRequirement")
    shadow_price_protein = protein_constr.Pi
    print(f"\nShadow price of protein constraint: ${shadow_price_protein:.4f} / g")

    # Relax protein constraint to ≥ 7.0g and resolve
    protein_constr.rhs = 7.0
    model.optimize()
    if model.status == GRB.OPTIMAL:
        cost_reduction = 8.0 * shadow_price_protein  # Or compare objective values directly
        print(f"\nAfter relaxing protein constraint to ≥ 7.0g, cost per can: ${model.objVal:.4f}")
        print(f"Cost reduction per can: ${8.0 * shadow_price_protein:.4f}")
else:
    print("Optimal solution not found for the model.")
