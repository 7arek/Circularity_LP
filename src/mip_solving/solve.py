from graph_utils import read_graph_from_dataset, print_graph
from mip_solver import solve_single_district_mip, print_solution, save_solution_csv


def solve(dataset_name: str, area_lower_bound: float = 0):
    """
    Solve the single district MIP model for the given dataset.
    :param dataset_name: Name of the dataset (e.g., 'issoire').
    :param area_lower_bound: Area lower bound for the district.
    :return: A tuple containing the solution (list of nodes in the district) and the Gurobi model object.
    """

    # Load the graph from the 'issoire' dataset
    graph = read_graph_from_dataset(dataset_name)

    # print_graph(graph)

    solution, m = solve_single_district_mip(graph, area_lower_bound)

    file_suffix = f"_LB={area_lower_bound}" if area_lower_bound > 0 else ""

    print_solution(m, solution, dataset_name, file_suffix=file_suffix)

    return solution, m


if __name__ == '__main__':
    # datasets = ["issoire", "avignon", "braunschweig", "karlsruhe", "neumuenster"]
    solve("issoire", area_lower_bound=0.1)
    # solve("avignon")
    # solve("braunschweig")
    # solve("karlsruhe")
    # solve("neumuenster")
    # solve("rheinruhr")
