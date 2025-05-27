import argparse

from libpysal import weights
import libpysal
import matplotlib
matplotlib.use('TkAgg')  # Use a standard backend (for pycharm)
import matplotlib.pyplot as plt
import networkx as nx
import geopandas
import numpy as np
import itertools
import pandas as pd

import argparse
import os


def writeGraphToCsv(graph, filename, ids=None):
    """Write a weighted NetworkX graph to a file using all attributes of the
    nodes.
    """

    # Ensure the directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    # Open a file for writing the vertices
    with open(filename + "_vertices.csv", "w") as file:
        # Get the attributes of the first node and use the keys as header
        file.write(",".join(graph.nodes[0].keys()))
        file.write("\n")

        # Write all nodes
        for idx, node in enumerate(graph.nodes(data=True)):
            # Cast the attributes to string and add a comma in between
            file.write(",".join([str(x) for x in node[1].values()]))
            file.write("\n")

    # Open a file for writing the edges
    with open(filename + "_edges.csv", "w") as file:
        # Write the header
        file.write("from_id,to_id,weight\n")
        # Write all edges
        for idx, edge in enumerate(graph.edges(data=True)):
            # Use the ids from the graph if no further information is given
            if ids is None:
                # Use the FID attribute of the nodes
                source = str(graph.nodes[edge[0]]["FID"])
                target = str(graph.nodes[edge[1]]["FID"])
            else:
                # Use the lookup table to provide the original ids
                source = str(ids[edge[0]])
                target = str(ids[edge[1]])
            weight = str(edge[2]["weight"])
            # Write the edge data to the file
            file.write(",".join([source, target, weight]))
            file.write("\n")


def visualizeGraph(graph, subdivision):
    """Visualize a connectivity graph of a planar subdivision with vertex IDs matching those in _vertices.txt."""

    # Use the same IDs as in writeGraphToTxt (first column of subdivision)
    ids = subdivision.iloc[:, 0].values
    id_map = dict(zip(graph.nodes, ids))

    # extract the centroids for connecting the regions
    centroids = np.column_stack((subdivision.centroid.x, subdivision.centroid.y))
    # Only assign positions to nodes that correspond to actual polygons (not -1)
    positions = {node: (x, y) for node, (x, y) in zip(graph.nodes, centroids) if node != -1}

    # plot with a nice basemap
    ax = subdivision.plot(linewidth=1, edgecolor="grey", facecolor="lightblue")
    ax.axis("off")
    # Draw only nodes with positions
    nx.draw(graph.subgraph(positions.keys()), positions, ax=ax, node_size=5, node_color="purple")

    # Add vertex IDs as labels (using the original IDs)
    for node, (x, y) in positions.items():
        ax.text(x, y, str(id_map[node]), fontsize=14, ha='center', va='center', color='red')


def processDataset(dataset):
    print(dataset)

    path = os.path.join("res", "roads-reduced", f"{dataset}.shp")

    subdivision = geopandas.read_file(path)
    # print(subdivision.crs)
    rook = weights.Rook.from_dataframe(subdivision)

    shared = []
    # Iterate over all nodes of the connectivity
    for source in rook.id_order:
        # First geometry
        poly1 = subdivision.geometry[source]
        # Ids of neighbors as array
        neighbor_ids = np.array(rook.neighbors[source], dtype=int)
        # Only select neighbors with id greater than source (use only one direction)
        neighbor_ids = neighbor_ids[neighbor_ids > source]
        # Skip if no neighbors left
        if neighbor_ids.size == 0:
            continue
        # Get the geometries of the neighbors
        neighbors = subdivision.geometry[neighbor_ids]
        # Lengths of the shared edges between the first poly and its neighbors
        dist = poly1.intersection(neighbors).length
        # Save the adjacencies
        for n, d in dist.items():
            shared.append([source, n, d])

    # Add the outside as a vertex with id -1
    outside_idx = subdivision.shape[0]  # Use the next free index as outside vertex
    # Find polygons that touch the exterior (boundary of the union of all polygons)
    union_geom = subdivision.unary_union
    exterior = union_geom.boundary
    for idx, poly in subdivision.iterrows():
        # If the polygon touches the exterior, add an edge to the outside vertex
        if poly.geometry.touches(exterior):
            # Use the length of the shared boundary with the exterior as weight
            shared_length = poly.geometry.boundary.intersection(exterior).length
            if shared_length > 0:
                shared.append([outside_idx, idx, shared_length])

    # Then, we can convert the graph to networkx object using the
    # .to_networkx() method.
    graph = rook.to_networkx()

    # Add the outside node with minimal attributes
    # Set outside_idx to the next free index
    graph.add_node(outside_idx)
    graph.nodes[outside_idx]["FID"] = -1
    graph.nodes[outside_idx]["area"] = 0

    # Write data from the polygons to the nodes
    for idx, poly in subdivision.iterrows():
        for col in subdivision:
            # Do not save the geometry column
            if col == "geometry":
                continue
            graph.nodes[idx][col] = poly[col]
        # Add an additional area column
        graph.nodes[idx]["area"] = poly.geometry.area

    # Add the computed edge weights to the graph
    graph.add_weighted_edges_from(shared)

    # The command assumes that the ids are in the first column
    # ids =  list(subdivision.iloc[:, 0])


    csv_path = os.path.join("res", "graphs", f"{dataset}", f"{dataset}")
    writeGraphToCsv(graph, csv_path)

    visualizeGraph(graph, subdivision)


parser = argparse.ArgumentParser(description="Path to data directory")
parser.add_argument('-d', '--dir', type=str, default=None, help='Path to the directory containing the streetmap files')

if __name__ == '__main__':
    from multiprocessing import Pool

    # datasets = [
    #     "avignon", "braunschweig", "issoire", "karlsruhe", "neumuenster",
    #     "F_NUTS3_UTM"
    # ]
    datasets = ["issoire"]
    # datasets = ["F_NUTS3_UTM"]
    # with Pool() as p:
    #     p.map(processDataset, datasets)

    for dataset in datasets:
        processDataset(dataset)
    plt.show()
