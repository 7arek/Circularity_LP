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