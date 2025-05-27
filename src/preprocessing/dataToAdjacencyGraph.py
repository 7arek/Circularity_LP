import argparse

from libpysal import weights
import libpysal
import matplotlib.pyplot as plt
import networkx as nx
import geopandas
import numpy as np
import itertools
import pandas as pd

import argparse
import os


def writeGraphToTxt(graph, filename, ids=None):
    """Write a weighted NetworkX graph to a file using all attributes of the 
    nodes.
    """

    # Open a file for writing the vertices
    with open(filename + "_vertices.txt", "w") as file:
        # Get the attributes of the first node and use the keys as header
        file.write(",".join(graph.nodes[0].keys()))
        file.write("\n")

        # Write all nodes
        for idx, node in enumerate(graph.nodes(data=True)):
            # Cast the attributes to string and add a comma in between
            file.write(",".join([str(x) for x in node[1].values()]))
            file.write("\n")

    # Open a file for writing the edges
    with open(filename + "_edges.txt", "w") as file:
        # Write the header
        file.write("from_id,to_id,weight\n")
        # Write all edges
        for idx, edge in enumerate(graph.edges(data=True)):
            # Use the ids from the graph if no further information is given
            if ids is None:
                source = str(edge[0])
                target = str(edge[1])
            else:
                # Use the lookup table to provide the original ids
                source = str(ids[edge[0]])
                target = str(ids[edge[1]])
            weight = str(edge[2]["weight"])
            # Write the edge data to the file
            file.write(",".join([source, target, weight]))
            file.write("\n")


def visualizeGraph(graph, subdivision):
    """Visualize a connectivity graph of a planar subdivision."""

    # extract the centroids for connecting the regions, which is
    # the average of the coordinates that define the polygon's boundary
    centroids = np.column_stack(
        (subdivision.centroid.x, subdivision.centroid.y))
    # To plot with networkx, we need to merge the nodes back to
    # their positions in order to plot in networkx
    positions = dict(zip(graph.nodes, centroids))

    # plot with a nice basemap
    ax = subdivision.plot(linewidth=1, edgecolor="grey", facecolor="lightblue")
    ax.axis("off")
    nx.draw(graph, positions, ax=ax, node_size=5, node_color="r")


def processDataset(dataset, path):
    print(dataset)

    if path is None:
        path = f"{dataset}/{dataset}.shp"
    else:
        path = f"{path}/{dataset}.shp"

    subdivision = geopandas.read_file(path)
    print(subdivision.crs)
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

    # Then, we can convert the graph to networkx object using the
    # .to_networkx() method.
    graph = rook.to_networkx()
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
    writeGraphToTxt(graph, path.replace(".shp", ""), ids=subdivision.iloc[:, 0])

    visualizeGraph(graph, subdivision)


parser = argparse.ArgumentParser(description="Path to data directory")
parser.add_argument('-d', '--dir', type=str, default=None, help='Path to the directory containing the streetmap files')

if __name__ == '__main__':
    from multiprocessing import Pool

    # datasets = [
    #     "avignon", "braunschweig", "issoire", "karlsruhe", "neumuenster",
    #     "F_NUTS3_UTM"
    # ]
    datasets = ["rheinruhr"]
    # datasets = ["F_NUTS3_UTM"]
    # with Pool() as p:
    #     p.map(processDataset, datasets)

    args = parser.parse_args()
    if args.dir is not None:
        if os.path.isdir(args.dir):
            print(f"Directory path is valid: {args.dir}")
            current_path = args.dir
        else:
            print(f"Invalid directory path: {args.dir}")
    else:
        print("No directory path provided, using default path")
        current_path = None

    for dataset in datasets:
        processDataset(dataset, current_path)
    plt.show()
