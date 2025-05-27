from graph_utils import read_graph_from_dataset, print_graph
from mip_solver import solve_single_district_mip, print_solution, save_solution_csv


def solve(dataset_name: str):
    """
    Solve the single district MIP model for the given dataset.
    :param dataset_name: Name of the dataset (e.g., 'issoire')
    :return: A tuple containing the solution (list of nodes in the district) and the Gurobi model object.
    """

    # Load the graph from the 'issoire' dataset
    graph = read_graph_from_dataset(dataset_name)

    # print_graph(graph)

    solution, m = solve_single_district_mip(graph)

    print_solution(m, solution, dataset_name)

    # Save the solution to a CSV file
    save_solution_csv(solution, dataset_name)

    return solution, m


if __name__ == '__main__':
    # datasets = ["issoire", "avignon", "braunschweig", "karlsruhe", "neumuenster"]
    solve("issoire")
    solve("avignon")
    solve("braunschweig")
    solve("karlsruhe")
    solve("neumuenster")
