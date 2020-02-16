from pulp import *

problem = LpProblem("example")

x_1 = LpVariable("x_1", cat="Binary")
x_2 = LpVariable("x_2", cat="Binary")
x_3 = LpVariable("x_3", cat="Binary")
x_4 = LpVariable("x_4", cat="Binary")
x_5 = LpVariable("x_5", cat="Binary")
x_6 = LpVariable("x_6", cat="Binary")

problem += LpAffineExpression([(x_1, 3), (x_2, 5), (x_3, 6), (x_4, 9), (x_5, 10), (x_6, 10)])

problem += LpAffineExpression([(x_1, -2), (x_2, 6), (x_3, -3), (x_4, 4), (x_5, 1), (x_6, -2)]) == 2
# problem += lpSum([-2 * x_1, 6 * x_2, -3 * x_3, 4 * x_4, x_5, -2 * x_6]) >= 2
problem += lpSum([-5 * x_1, -3 * x_2, x_3, 3 * x_4, -2 * x_5, x_6]) >= -2
problem += lpSum([5 * x_1, -1 * x_2, 4 * x_3, -2 * x_4, 2 * x_5, -1 * x_6]) >= 3

print(problem)

# problem.solve()
#
# print("Status: " + LpStatus[problem.status])
#
# for v in problem.variables():
#     print(v.name, "=", v.varValue)