import os

import networkx as nx
import gurobipy as gp
from gurobipy import GRB

from mip_build_district import build_single_district_mip

"""
Code based on "Political districting to optimize the Polsby-Popper compactness score with application to  voting
rights"
"""


def solve_single_district_mip(DG: nx.DiGraph, area_lower_bound: float = 0) -> tuple[list[int], gp.Model] | None:
    """
    Solve the single district MIP model.
    :param DG: Directed graph representing the districting problem, where nodes have 'node_weight' and 'boundary_perim' attributes,
                    and edges have 'shared_perim' attribute.
    :param area_lower_bound: Lower bound for the area.
    :return: A tuple containing the list of nodes in the district and the Gurobi model object.
    TODO: I dont know if this is correctly implemented (e.g. if the hyperparameters are set correctly).
    """
    m = build_single_district_mip(DG, area_lower_bound=area_lower_bound)

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


def print_solution(m: gp.Model, solution: list[int], dataset_name: str, print_all_vars:
bool = True, file_suffix : str = None) -> None:
    """
    Print the solution of the MIP model and save it to a file.
    """
    output_summary = []
    output_summary.append("######Solution summary######")
    output_summary.append(f"District nodes: {solution}")
    pp_inverse = float(m._z.x)
    output_summary.append(f"Polsby-Popper score: {'infinity' if pp_inverse == 0 else f'{1 / pp_inverse:.4f}'}")
    output_summary.append(f"Inverse Polsby-Popper score (Objective value): {m._z.x:.4f}")
    output_summary.append(f"Area: {m._A.x:.4f}")
    output_summary.append(f"Perimeter: {m._P.x:.4f}")
    output_summary.append(f"Model status: {m.status}")  # Print the model status

    output_vars = []
    if print_all_vars:
        output_vars.append("######All Variables######")
        for v in m.getVars():
            output_vars.append(f"{v.varName}: {v.x:.4f}")

    # Save the output string to a file
    os.makedirs(os.path.join("data", "solutions"), exist_ok=True)
    solutions_path = os.path.join("data", "solutions", f"{dataset_name}{file_suffix}.txt")
    with open(solutions_path, "w") as file:
        file.write("\n".join(output_summary + output_vars))

    # Print only the solution summary to the console
    print("\n".join(output_summary))

