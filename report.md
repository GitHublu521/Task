# Report

## Task 1: Cat Food Optimization Problem

### 1.1 Mathematical Formulation

#### Decision Variables
- $x_1$ = Beef (g)
- $x_2$ = Cereal (g)  
- $x_3$ = Chicken (g)
- $x_4$ = Gel (g)
- $x_5$ = Fish meal (g)
- $x_6$ = Additive (g)

#### Objective Function
Minimize cost per can:
$$\min Z = 0.005x_1 + 0.01x_2 + 0.002x_3 + 0.001x_4 + 0.008x_5 + 0.006x_6$$

#### Constraints

1. **Total weight**:
   $$x_1 + x_2 + x_3 + x_4 + x_5 + x_6 = 100$$

2. **Protein** (≥ 8g):
   $$0.20x_1 + 0.12x_2 + 0.25x_3 + 0.01x_4 + 0.60x_5 + 0.00x_6 \geq 8$$

3. **Fat** (≤ 6g):
   $$0.10x_1 + 0.08x_2 + 0.15x_3 + 0.00x_4 + 0.02x_5 + 0.00x_6 \leq 6$$

4. **Fibre** (≤ 2g):
   $$0.005x_1 + 0.01x_2 + 0.01x_3 + 0.00x_4 + 0.02x_5 + 0.00x_6 \leq 2$$

5. **Salt** (≤ 0.4g):
   $$0.005x_1 + 0.002x_2 + 0.003x_3 + 0.001x_4 + 0.01x_5 + 0.30x_6 \leq 0.4$$

6. **Non-negativity**:
   $$x_1, x_2, x_3, x_4, x_5, x_6 \geq 0$$

### 1.2 Solver Output
Optimal solution found
Objective value: 0.5200

Variable Values:

Beef (x1): 60.00 g

Gel (x4): 40.00 g

Cereal (x2): 0.00 g

Chicken (x3): 0.00 g

Fish meal (x5): 0.00 g

Additive (x6): 0.00 g


### 1.3 Results Interpretation

#### Optimal Recipe
- **Beef**: 60.00 g
- **Gel**: 40.00 g
- **Minimum cost per can**: $0.5200

#### Constraint Verification
| Constraint | Calculation | Status |
|------------|-------------|--------|
| Total weight | 60 + 40 = 100 g | ✓ Satisfied |
| Protein | 60 × 0.20 = 12 g (≥ 8 g) | ✓ Satisfied |
| Fat | 60 × 0.10 = 6 g (≤ 6 g) | ✓ Satisfied (binding) |
| Fibre | 60 × 0.005 = 0.3 g (≤ 2 g) | ✓ Satisfied |
| Salt | 60 × 0.005 = 0.3 g (≤ 0.4 g) | ✓ Satisfied |

#### Shadow Price Analysis

**Protein constraint shadow price**: $0.0000/g

**Sensitivity test**: Relaxing protein requirement to ≥ 7.0 g
- New optimal cost: $0.5200
- Cost reduction: $0.0000

**Interpretation**: The protein constraint is **non-binding** in the optimal solution. The current recipe provides 12g of protein, which exceeds the 8g requirement. Therefore, relaxing this constraint has no effect on the optimal solution or cost. The solution is limited by other constraints (particularly the fat constraint, which is exactly at its upper bound).

---

## Task 2: Fixed-Charge Network Flow Problem

### 2.1 Mathematical Formulation

#### Model Type
Mixed Integer Programming (MIP)

#### Decision Variables

1. **Continuous Flow Variables**
   $$x_{a,c} \geq 0 \quad (\forall a \in A, c \in C)$$
   - Meaning: Quantity of product $c$ transported on arc $a$ (units)
   - Property: Non-negative continuous variables representing actual shipment quantities

2. **Binary Arc Opening Variables**
   $$y_a \in \{0, 1\} \quad (\forall a \in A)$$
   - Meaning: Whether arc $a$ is opened ($y_a = 1$) or not ($y_a = 0$)
   - Property: Binary integer variables, which make this a MIP problem

#### Objective Function
Minimize total cost:
$$\min Z = \sum_{a \in A} f_a \cdot y_a + \sum_{a \in A} \sum_{c \in C} u_{a,c} \cdot x_{a,c}$$

- **First term**: $\sum_{a \in A} f_a \cdot y_a$ - Fixed costs for all opened routes
- **Second term**: $\sum_{a \in A} \sum_{c \in C} u_{a,c} \cdot x_{a,c}$ - Variable transportation costs for all products

#### Constraints
The model includes four types of core constraints:
- Flow conservation
- Capacity limits
- Variable logic constraints (linking $x_{a,c}$ and $y_a$)
- Supply and demand balance

### 2.2 LP Relaxation

#### Variable Adjustment
Relax binary variables $y_a \in \{0, 1\}$ to continuous variables:
$$0 \leq y_a \leq 1 \quad (\forall a \in A)$$

All other constraints (flow conservation, capacity limits, non-negativity) remain unchanged.

### 2.3 Solver Output
Optimal solution found (MIP)
Objective value: $5,410.00

Cost Breakdown:

Fixed costs: $3,000.00

Transportation costs: $2,410.00

Opened Arcs:

W1 → S2

W1 → S3

W2 → S1

W2 → S2

### 2.4 Results Interpretation

#### Transportation Plan (units)

| Route | Electronics | Furniture | Total |
|-------|-------------|-----------|-------|
| W1 → S2 | 40.0 | 10.0 | 50.0 |
| W1 → S3 | 40.0 | 60.0 | 100.0 |
| W2 → S1 | 50.0 | 40.0 | 90.0 |
| W2 → S2 | 20.0 | 40.0 | 60.0 |

#### Supply and Demand Verification

All warehouse supplies are fully utilized, and all store demands are completely satisfied:

**Warehouse Outbound**:
- W1: Electronics (80/80), Furniture (70/70)
- W2: Electronics (70/70), Furniture (80/80)

**Store Inbound**:
- S1: Electronics (50/50), Furniture (40/40)
- S2: Electronics (60/60), Furniture (50/50)
- S3: Electronics (40/40), Furniture (60/60)

### 2.5 LP Relaxation and Integrality Gap

#### LP Relaxation Solution
Relaxing binary variables $y_a$ to continuous variables $0 \leq y_a \leq 1$ yields:
- **LP relaxation objective value**: $3,760.00

#### Integrality Gap Calculation
$$\text{Integrality Gap} = \frac{\text{MIP optimal value} - \text{LP relaxation value}}{\text{MIP optimal value}} \times 100\%$$
$$\text{Integrality Gap} = \frac{5410 - 3760}{5410} \times 100\% \approx 43.88\%$$

**Interpretation**: Due to the integer constraint requiring routes to be either fully opened or closed, the actual executable solution (MIP) costs 43.88% higher than the theoretical lower bound (LP relaxation). The $y$ values in the LP relaxation (e.g., W1-S2: 0.250) are only theoretical and cannot be implemented directly.

### 2.6 Conclusions for Task 2

1. The optimal solution opens 4 routes, satisfying all supply and demand constraints with a total cost of $5,410.00.
2. Fixed costs account for over 55% of the total cost, making them the main cost component.
3. The 43.88% integrality gap indicates that integer decisions significantly impact the cost, and the LP relaxation serves only as a theoretical lower bound reference.

---

## Task 3: Employee Scheduling Problem

### 3.1 Mathematical Formulation

#### Model Type
Mixed Integer Linear Programming (MILP)

#### Objective Function
Minimize total daily labor cost:
$$\min \sum_{e \in E} \sum_{h \in H} w_e \cdot y_{e,h}$$

Where:
- $w_e$ = hourly wage of employee $e$
- $y_{e,h}$ = 1 if employee $e$ works in hour $h$, 0 otherwise

#### Decision Variables

1. **Shift Selection Variables (Binary)**
   $$x_{e,s,d} \in \{0, 1\}$$
   - $x_{e,s,d} = 1$: Employee $e$ starts a shift at hour $s$ with duration $d$ hours
   - $x_{e,s,d} = 0$: Employee does not select this shift

2. **Hour Coverage Variables (Binary)**
   $$y_{e,h} \in \{0, 1\}$$
   - $y_{e,h} = 1$: Employee $e$ works during hour $h$
   - $y_{e,h} = 0$: Employee does not work during hour $h$

#### Constraints
The model includes five types of constraints:
- Shift continuity and hour coverage linkage
- Shift duration limits
- Working time window constraints
- Hourly staffing requirements
- Variable non-negativity and integrality

### 3.2 Solver Output
Optimal solution found (MILP)
Gap: 0.00% (Global optimal)

Daily minimum total cost: $4,700.00
Total scheduled hours: 115 hours
Employee hour utilization rate: 92.7%

### 3.3 Results Interpretation

#### (1) Core Economic Indicators

| Metric | Value |
|--------|-------|
| Minimum Daily Total Cost | $4,700.00 |
| Total Scheduled Hours | 115 hours |
| Employee Hour Utilization | 92.7% |
| Optimality Gap | 0.00% (Global optimal) |

#### (2) Key Staffing Strategy (Cost Optimization Logic)

| Employee Type | Wage Range | Staffing Pattern | Example |
|---------------|------------|------------------|---------|
| Low-wage Core | $30 | Full shifts (8 hours), covering peak periods | SMITH: 06:00-14:00 |
| Medium-wage Supplementary | $35-$45 | Full shifts, covering midday/afternoon peaks | MILLER: 08:00-16:00 |
| High-wage Gap-fillers | $50-$60 | Short shifts, only filling night/critical low-demand periods | ANDERSON: 00:00-02:00 |

#### (3) Constraint Satisfaction Verification

All hourly staffing requirements are **exactly met**, with no shortages and no surplus:

| Time Period | Minimum Required | Actual Staffed | Status |
|-------------|------------------|----------------|--------|
| 00-01 | 1 | 1 | ✓ |
| 08-09 | 9 | 9 | ✓ |
| 22-23 | 2 | 2 | ✓ |

### 3.4 Conclusions for Task 3

1. **Cost Optimality**: The model found a global optimal solution (Gap = 0%), with $4,700 being the theoretical minimum daily labor cost.

2. **Resource Efficiency**: The 92.7% hour utilization rate achieves optimal resource allocation through "more shifts for low-wage employees, fewer shifts for high-wage employees."

3. **Implementation Feasibility**: The scheduling plan fully complies with all business constraints (continuous shifts, duration limits, time windows) and can be directly implemented.

---
