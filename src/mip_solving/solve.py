import os

from graph_utils import read_graph_from_dataset, print_graph
from mip_solver import solve_single_district_mip, print_and_save_solution
from solution_plotting.solution_plotter import plot_shapefile_with_highlights


def solve(dataset_name: str, area_lower_bound: float = 0):
    """
    Solve the single district MIP model for the given dataset.
    :param dataset_name: Name of the dataset (e.g., 'issoire').
    :param area_lower_bound: Area lower bound for the district.
    :return: A tuple containing the solution (list of nodes in the district) and the Gurobi model object.
    """

    # Check if the solution folder already exists
    solution_name = f"{dataset_name}{'_LB=' + str(area_lower_bound) if area_lower_bound > 0 else ''}"
    solution_folder = f"data/solutions/{solution_name}"
    if os.path.exists(solution_folder):
        print(f"Solution folder '{solution_name}' already exists. Skipping solving for {dataset_name}.")
        return None, None

    # Load the graph from the 'issoire' dataset
    graph = read_graph_from_dataset(dataset_name)

    # print_graph(graph)

    graph.graph['dataset_name'] = dataset_name
    graph.graph['area_lower_bound'] = area_lower_bound

    solution, m = solve_single_district_mip(graph, area_lower_bound)

    file_suffix = f"_LB={area_lower_bound}" if area_lower_bound > 0 else ""

    print_and_save_solution(m, solution, dataset_name, file_suffix=file_suffix)

    plot_shapefile_with_highlights(dataset_name, highlight_color="red", base_color="lightblue", marker_color="orange", file_suffix=file_suffix)

    return solution, m


if __name__ == '__main__':
    datasets = ["issoire", "avignon", "braunschweig", "karlsruhe", "neumuenster","rheinruhr"]
    for dataset in datasets:
        print(f"Solving {dataset}...")
        solve(dataset, area_lower_bound=0)
        solve(dataset, area_lower_bound=1e6)
        print(f"Finished solving {dataset}.\n")
    # solve("avignon", area_lower_bound=1e6)
    # solve("avignon", area_lower_bound=1e-4)
    # solve("avignon")
    # solve("braunschweig")
    # solve("karlsruhe")
    # solve("neumuenster")
    # solve("rheinruhr")
