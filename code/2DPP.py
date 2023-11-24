'''solve 2-dimensional packing problem with gurobi'''

from gurobipy import GRB, Model, quicksum
import matplotlib.pyplot as plt

name = '2DPP'
model = Model(name)

# length and width of rectangle
rectangle_set = [{"width": 24, "height": 24, "rotatable": True},  # robot {"width": 240, "height": 240, "rotatable": True}
                 {"width": 100, "height": 100, "rotatable": True},  # table
                 {"width":  50, "height":  30, "rotatable": True},  # parts 1
                 {"width":  50, "height":  30, "rotatable": True},  # parts 2
                 {"width":  50, "height":  40, "rotatable": True},  # parts 3
                 {"width":  50, "height":  40, "rotatable": True},  # parts 4
                 ]

num_rect = len(rectangle_set)

# W_UB is the sum of all widths in the rectangle set
W_UB = sum([rectangle['width'] for rectangle in rectangle_set])
H_UB = sum([rectangle['height'] for rectangle in rectangle_set])

# add coordinate variables and rotation variables
for i in range(num_rect):
    model.addVar(name=f'x_{i}', lb=0, ub=W_UB)
    model.addVar(name=f'y_{i}', lb=0, ub=H_UB)
    model.addVar(name=f'W', lb=0, ub=W_UB)
    model.addVar(name=f'H', lb=0, ub=H_UB)

# add position binary variables
for i in range(num_rect):
    for j in range(num_rect):
        if i != j:
            model.addVar(name=f'u_{i}_{j}', vtype=GRB.BINARY)
            model.addVar(name=f'v_{i}_{j}', vtype=GRB.BINARY)

model.update()

# add objective function
model.setObjective(model.getVarByName(
    'W') * model.getVarByName('H'), GRB.MINIMIZE)

# add constraints
for i in range(num_rect):
    for j in range(num_rect):
        if i != j:
            # relative position constraints i and j in x direction
            model.addConstr(model.getVarByName(f'x_{i}') + rectangle_set[i]['width'] <= model.getVarByName(
                f'x_{j}') + W_UB * (1 - model.getVarByName(f'u_{i}_{j}')))
            # relative position constraints i and j in y direction
            model.addConstr(model.getVarByName(f'y_{i}') + rectangle_set[i]['height'] <= model.getVarByName(
                f'y_{j}') + H_UB * (1 - model.getVarByName(f'v_{i}_{j}')))
            # at least one of u_ij, v_ij, u_ji, v_ji is 1
            model.addConstr(model.getVarByName(f'u_{i}_{j}') + model.getVarByName(f'v_{i}_{j}') + model.getVarByName(
                f'u_{j}_{i}') + model.getVarByName(f'v_{j}_{i}') >= 1)
            # if u_ij = 1, then u_ji = 0
            # model.addConstr(model.getVarByName(f'u_{i}_{j}') <= 1 - model.getVarByName(f'u_{j}_{i}'))
            # # if v_ij = 1, then v_ji = 0
            # model.addConstr(model.getVarByName(f'v_{i}_{j}') <= 1 - model.getVarByName(f'v_{j}_{i}'))
            model.addConstr(model.getVarByName(f'x_{i}') <= model.getVarByName(
                'W') - rectangle_set[i]['width'])
            model.addConstr(model.getVarByName(f'y_{i}') <= model.getVarByName(
                'H') - rectangle_set[i]['height'])

# optimize
model.params.NonConvex = 2
model.optimize()
# model.write(f'{name}.lp')

# print solution
print(f'W = {model.getVarByName("W").X}')
print(f'H = {model.getVarByName("H").X}')

for i in range(num_rect):
    print(f'x_{i} = {model.getVarByName(f"x_{i}").X}')
    print(f'y_{i} = {model.getVarByName(f"y_{i}").X}')

for i in range(num_rect):
    for j in range(num_rect):
        if i != j:
            print(f'u_{i}_{j} = {model.getVarByName(f"u_{i}_{j}").X}')
            print(f'v_{i}_{j} = {model.getVarByName(f"v_{i}_{j}").X}')

# plot solution
plt.figure()
ax = plt.gca()
ax.set_xlim([0, W_UB])
ax.set_ylim([0, H_UB])
# rectangles have black borders and gray faces
for i in range(num_rect):
    x = model.getVarByName(f'x_{i}').X
    y = model.getVarByName(f'y_{i}').X
    ax.add_patch(plt.Rectangle(
        (x, y), rectangle_set[i]['width'], rectangle_set[i]['height'], edgecolor='black', facecolor='gray'))
    ax.text(x + rectangle_set[i]['width'] / 2, y + rectangle_set[i]['height'] / 2,
            str(i), horizontalalignment='center', verticalalignment='center')

plt.show()
