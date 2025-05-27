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
    :param DG: Directed graph representing the districting problem, where nodes have 'node_weight' and 'boundary_perim' attributes,
                    and edges have 'shared_perim' attribute.
    :return: A tuple containing the list of nodes in the district and the Gurobi model object.
    TODO: I dont know if this is correctly implemented (e.g. if the hyperparameters are set correctly).
    """
    m = build_single_district_mip(DG)

    # Set time limit for the optimization
    m.Params.TimeLimit = 3600  # 1 hour

    # Limit to 1 Thread
    m.Params.Threads = 1

    # Optimize the model
    m.optimize(m._callback)

    # Check if a solution was found
    if not m.status == GRB.OPTIMAL or m.status == GRB.TIME_LIMIT:
        print("ERROR: !!!Something went wrong when solving the MIP model.!!!")

    # Extract the solution
    solution = [i for i in DG.nodes if m._x[i].x > 0.5]
    return solution, m


def print_solution(m: gp.Model, solution: list[int], print_all_vars : bool = True) -> None:
    """
    Print the solution of the MIP model.
    """
    print("######Optimal solution found######")

    if print_all_vars:
        print(f"Printing all variables:")
        for v in m.getVars():
            print(f"{v.varName}: {v.x:.4f}")

    print("######Solution summary######")
    print(f"District nodes: {solution}")
    pp_inverse = float(m._z.x)
    print(f"Polsby-Popper score: {'infinity' if pp_inverse == 0 else f'{1/pp_inverse:.4f}'}")
    print(f"Inverse Polsby-Popper score (Objective value): {m._z.x:.4f}")
    print(f"Area: {m._A.x:.4f}")
    print(f"Perimeter: {m._P.x:.4f}")
    print(f"Model status: {m.status}")  # Print the model status


