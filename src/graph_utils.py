import networkx as nx
import os
import csv


def read_graph_from_dataset(dataset : str) -> nx.DiGraph:
    """
    Reads a dataset from datasets/{dataset} and loads it as a networkx DiGraph.

    :param dataset: Name of the dataset (e.g., 'issoire')
    :return: A networkx.DiGraph object
    """
    # Construct the file path
    file_path = os.path.join("datasets", dataset, f"{dataset}_edges.csv")

    # Initialize a directed graph
    graph = nx.DiGraph()

    # Read the CSV file and add edges to the graph
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header line
        for row in reader:
            source, target, weight = int(row[0]), int(row[1]), float(row[2])
            graph.add_edge(source, target, weight=weight)

    return graph