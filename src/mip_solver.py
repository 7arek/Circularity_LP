import networkx as nx
import gurobipy as gp
from gurobipy import GRB

from district import build_single_district_mip

"""
Code based on "Political districting to optimize the Polsby-Popper compactness score with application to  voting
rights"
"""


def solve_single_district_mip(DG: nx.DiGraph) -> tuple[list[int], gp.Model] | None:
    """
    Solve the single district MIP model.
    TODO: I dont know if this is correctly implemented.
    """
    m = build_single_district_mip(DG)

    # Set time limit for the optimization
    m.Params.TimeLimit = 3600  # 1 hour

    # Limit to 1 Thread
    m.Params.Threads = 1

    # Optimize the model
    m.optimize(m._callback)

    # Check if a solution was found
    print("Model status:", m.status)
    if m.status == GRB.OPTIMAL or m.status == GRB.TIME_LIMIT:
        # Extract the solution
        solution = [i for i in DG.nodes if m._x[i].x > 0.5]
        return solution, m
    else:
        print("No optimal solution found.")
        return None


def print_solution(m: gp.Model, solution: list[int]) -> None:
    """
    Print the solution of the MIP model.
    """
    print("######Optimal solution found######")
    print(f"District nodes: {solution}")
    pp_inverse = float(m._z.x)
    print(f"Polsby-Popper score: {'infinity' if pp_inverse == 0 else f'{1/pp_inverse:.4f}'}")
    print(f"Polsby-Popper score (inverse): {m._z.x:.4f}")
    print(f"Area: {m._A.x:.4f}")
    print(f"Perimeter: {m._P.x:.4f}")
    print(f"Objective value: {m.objVal:.4f}")
    print(f"Model status: {m.status}")  # Print the model status
    print(f"DEBUGGING INFO:")
    for v in m.getVars():
        print(f"{v.varName}: {v.x:.4f}")

