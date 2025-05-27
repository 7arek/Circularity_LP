from graph_utils import read_graph_from_dataset, print_graph
from mip_solver import solve_single_district_mip, print_solution


def solve(dataset: str):
    """
    Solve the single district MIP model for the given dataset.
    :param dataset: Name of the dataset (e.g., 'issoire')
    :return: A tuple containing the solution (list of nodes in the district) and the Gurobi model object.
    """

    # Load the graph from the 'issoire' dataset
    graph = read_graph_from_dataset(dataset)

    # print_graph(graph)

    solution, m = solve_single_district_mip(graph)

    print_solution(m, solution)

    return solution, m


if __name__ == '__main__':
    solve("issoire")