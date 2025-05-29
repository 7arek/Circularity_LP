import geopandas as gpd
import matplotlib
matplotlib.use('TkAgg')  # Use a standard backend (for pycharm)
import matplotlib.pyplot as plt
import os


def plotShapefileWithHighlights(shapefile_path, solution_path, highlight_color="red", base_color="lightblue", marker_color="black", marker_size=50):
    """
    Plots a shapefile and highlights specific polygons based on a solution file.
    Adds markers next to highlighted polygons for better visibility.

    :param shapefile_path: Path to the shapefile (.shp).
    :param solution_path: Path to the solution file (.csv) containing polygon IDs to highlight.
    :param highlight_color: Color for highlighted polygons.
    :param base_color: Color for non-highlighted polygons.
    :param marker_color: Color for the markers.
    :param marker_size: Size of the markers.
    """
    # Load the shapefile
    subdivision = gpd.read_file(shapefile_path)

    # Load the solution file (IDs to highlight)
    with open(solution_path, "r") as file:
        highlighted_ids = set(map(int, file.readline().strip().strip("[]").split(",")))


    # Add a column to indicate whether a polygon should be highlighted
    if "FID" in subdivision.columns:
        subdivision["highlight"] = subdivision["FID"].isin(highlighted_ids)
    else:
        subdivision["highlight"] = subdivision.index.isin(highlighted_ids)

    # Plot the shapefile
    ax = subdivision.plot(
        linewidth=1,
        edgecolor="grey",
        facecolor=subdivision["highlight"].map({True: highlight_color, False: base_color}),
    )

    # Add markers for highlighted polygons
    highlighted_centroids = subdivision[subdivision["highlight"]].geometry.centroid
    for centroid in highlighted_centroids:
        ax.scatter(centroid.x, centroid.y, color=marker_color, s=marker_size, zorder=5)

    ax.axis("off")
    ax.set_title("Highlighted Polygons with Markers", fontsize=16, pad=20)

    # Show the plot
    plt.show()


if __name__ == '__main__':
    # dataset_name = "avignon"
    # dataset_name = "braunschweig"
    # dataset_name = "issoire"
    # dataset_name = "karlsruhe"
    # dataset_name = "neumuenster"
    # shapefile_path = os.path.join("data", "shape", "roads-reduced", f"{dataset_name}.shp")
    # solution_path = os.path.join("data", "solutions", f"{dataset_name}_vertices.csv")
    # plotShapefileWithHighlights(shapefile_path, solution_path)



    dataset_name = "rheinruhr"
    shapefile_path = os.path.join("data", "shape", "rheinruhr", f"{dataset_name}.shp")
    solution_path = os.path.join("data", "solutions", f"{dataset_name}_vertices.csv")
    plotShapefileWithHighlights(shapefile_path, solution_path)