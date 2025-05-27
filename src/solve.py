from graph_utils import read_graph_from_dataset


def solve():
    # Load the graph from the 'issoire' dataset
    graph = read_graph_from_dataset("issoire")

    # Print the edges with weights
    for u, v, data in graph.edges(data=True):
        print(f"Edge from {u} to {v} with weight {data['weight']}")



if __name__ == '__main__':
    solve()