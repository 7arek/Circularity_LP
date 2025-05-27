import networkx as nx
import os
import csv


def read_graph_from_dataset(dataset : str) -> nx.DiGraph:
    """
    Reads a dataset from graphs/{dataset} and loads it as a networkx DiGraph.
    Loads the networkx Graph in the correct format for our MIP solver.

    :param dataset: Name of the dataset (e.g., 'issoire')
    :return: A networkx.DiGraph object representing the graph from the dataset
    """

    # Construct the file paths
    edges_file_path = os.path.join("res","graphs", dataset, f"{dataset}_edges.csv")
    vertices_file_path = os.path.join("res","graphs", dataset, f"{dataset}_vertices.csv")

    # Initialize a directed graph
    graph = nx.DiGraph()

    # Read the vertices file and add vertex weights as attributes
    with open(vertices_file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header line
        for row in reader:
            vertex, weight = int(row[0]), float(row[1])
            if vertex != -1:  # Skip outside vertex
                graph.add_node(vertex, node_weight=weight, boundary_node=False)

    # Read the CSV file and add edges to the graph
    with open(edges_file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header line
        for row in reader:
            source, target, weight = int(row[0]), int(row[1]), float(row[2])

            # Handle the case where source or target is -1 (outside vertex)
            if source == -1 or target == -1:
                valid_vertex = source if source != -1 else target
                graph.nodes[valid_vertex]['boundary_node'] = True
                graph.nodes[valid_vertex]['boundary_perim'] = weight
            else:
                graph.add_edge(source, target, shared_perim=weight)
                graph.add_edge(target, source, shared_perim=weight)

    return graph


def print_graph(graph: nx.DiGraph):
    """
    Prints the graph in a readable format.

    :param graph: A networkx.DiGraph object
    """
    print("Nodes:")
    for node, data in graph.nodes(data=True):
        print(f"Node {node}: {data}")

    print("\nEdges:")
    for source, target, data in graph.edges(data=True):
        print(f"Edge from {source} to {target} with weight {data['weight']}")