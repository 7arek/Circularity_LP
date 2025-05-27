from graph_utils import read_graph_from_dataset, print_graph
from mip_solver import solve_single_district_mip


def solve(dataset: str):
    # Load the graph from the 'issoire' dataset
    graph = read_graph_from_dataset(dataset)

    # print_graph(graph)

    solve_single_district_mip(graph)


if __name__ == '__main__':
    solve("issoire")