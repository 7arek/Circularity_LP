import geopandas as gpd
import matplotlib
matplotlib.use('TkAgg')  # Use a standard backend (for pycharm)
import matplotlib.pyplot as plt
import os



def plotShapefileWithHighlights(shapefile_path, solution_path, highlight_color="red", base_color="lightblue"):
    """
    Plots a shapefile and highlights specific polygons based on a solution file.

    :param shapefile_path: Path to the shapefile (.shp).
    :param solution_path: Path to the solution file (.csv) containing polygon IDs to highlight.
    :param highlight_color: Color for highlighted polygons.
    :param base_color: Color for non-highlighted polygons.
    """
    # Load the shapefile
    subdivision = gpd.read_file(shapefile_path)

    # Load the solution file (IDs to highlight)
    with open(solution_path, "r") as file:
        highlighted_ids = set(map(int, file.readline().strip("[]").split(",")))

    # Add a column to indicate whether a polygon should be highlighted
    subdivision["highlight"] = subdivision["FID"].isin(highlighted_ids)

    # Plot the shapefile
    ax = subdivision.plot(
        linewidth=1,
        edgecolor="grey",
        facecolor=subdivision["highlight"].map({True: highlight_color, False: base_color}),
    )
    ax.axis("off")
    ax.set_title("Highlighted Polygons", fontsize=16, pad=20)

    # Show the plot
    plt.show()

if __name__ == '__main__':
    shapefile_path = os.path.join("data", "shape", "roads-reduced", "avignon.shp")
    solution_path = os.path.join("data", "solutions", "avignon_vertices.csv")
    plotShapefileWithHighlights(shapefile_path, solution_path)

