import csv
import os


def write_graph_to_csv(input_file, vertices_file, edges_file):
    """
    Read a graph from a text file and write it to CSV files for vertices and edges.

    :param input_file: Path to the input text file containing the graph data.
    :param vertices_file: Path to the output CSV file for vertices.
    :param edges_file: Path to the output CSV file for edges.
    """

    # Initialize lists to store vertices and edges
    vertices = []
    edges = []

    # Read the input file
    with open(input_file, 'r') as file:
        lines = file.readlines()

    # Process the file
    for line in lines[1:]:  # Skip the header
        parts = line.strip().split()
        if parts[0] == 'v':  # Vertex line
            vertex_id = int(parts[1])
            weight = float(parts[2])
            vertices.append([vertex_id, weight])
        elif parts[0] == 'e':  # Edge line
            from_id = int(parts[1])
            to_id = int(parts[2])
            weight = float(parts[3])
            edges.append([from_id, to_id, weight])


    # Check if all edges are symmetric
    edge_dict = {(edge[0], edge[1]): edge[2] for edge in edges}
    for edge in edges:
        if (edge[1], edge[0]) not in edge_dict or edge_dict[(edge[1], edge[0])] != edge[2]:
            raise ValueError(f"Edge ({edge[0]}, {edge[1]}) is not symmetric.")


    # Only save edges from smaller to larger vertex IDs to ensure symmetry
    edges = [[min(edge[0], edge[1]), max(edge[0], edge[1]), edge[2]] for edge in edges]

    # Sort vertices and edges
    vertices.sort(key=lambda x: x[0])  # Sort vertices by ID
    edges.sort(key=lambda x: (x[0], x[1]))  # Sort edges by from_id, then to_id

    #Create the directory if it does not exist
    os.makedirs(os.path.dirname(vertices_file), exist_ok=True)

    # Write vertices to CSV
    with open(vertices_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['FID', 'area'])  # Header
        writer.writerows(vertices)

    # Write edges to CSV
    with open(edges_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['from_id', 'to_id', 'weight'])  # Header
        writer.writerows(edges)


if __name__ == '__main__':
    # File paths
    input_file = 'data/graphs/rheinruhr_joshua/rheinruhr_merged_result_dual.txt'
    vertices_file = 'data/graphs/rheinruhr/rheinruhr_vertices.csv'
    edges_file = 'data/graphs/rheinruhr/rheinruhr_edges.csv'

    # Write the graph to CSV files
    write_graph_to_csv(input_file, vertices_file, edges_file)