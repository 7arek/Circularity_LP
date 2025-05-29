import geopandas as gpd
import matplotlib
matplotlib.use('TkAgg')  # Use a standard backend (for pycharm)
import matplotlib.pyplot as plt
import os
import re


def plot_shapefile_with_highlights(dataset_name, highlight_color="red", base_color="lightblue",
                                   marker_color="orange", file_suffix=""):
    """
    Plots a shapefile and highlights specific polygons based on a solution file.
    Adds markers next to highlighted polygons for better visibility.

    :param dataset_name: Name of the dataset (e.g., 'avignon', 'issoire', etc.).
    :param highlight_color: Color for highlighted polygons.
    :param base_color: Color for non-highlighted polygons.
    :param marker_color: Color for the markers.
    """
    if dataset_name == "rheinruhr":
        shapefile_path = os.path.join("data", "shape", "rheinruhr", f"{dataset_name}.shp")
    else:
        shapefile_path = os.path.join("data", "shape", "roads-reduced", f"{dataset_name}.shp")
    solution_path = os.path.join("data", "solutions",f"{dataset_name}{file_suffix}", f"{dataset_name}{file_suffix}.txt")
    # Load the shapefile
    subdivision = gpd.read_file(shapefile_path)

    # Load the solution file (IDs to highlight)
    with open(solution_path, "r") as file:
        highlighted_ids = set(map(int, re.findall(r'\d+', file.readlines()[1])))


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
    # Calculate a bounding circle around all highlighted areas
    highlighted_bounds = subdivision[subdivision["highlight"]].geometry.total_bounds
    circle_center_x = (highlighted_bounds[0] + highlighted_bounds[2]) / 2
    circle_center_y = (highlighted_bounds[1] + highlighted_bounds[3]) / 2
    circle_radius = max(
        highlighted_bounds[2] - highlighted_bounds[0],
        highlighted_bounds[3] - highlighted_bounds[1]
    )
    image_size = max(subdivision.geometry.total_bounds[2] - subdivision.geometry.total_bounds[0], subdivision.geometry.total_bounds[3] - subdivision.geometry.total_bounds[1])
    circle_radius = max(circle_radius, 0.02 * image_size)

    # Add a circle around all highlighted areas
    circle = plt.Circle(
        (circle_center_x, circle_center_y),
        circle_radius,
        color=marker_color,
        fill=False,
        linewidth=2,
        zorder=5
    )
    ax.add_artist(circle)

    ax.axis("off")
    ax.axis("off")
    ax.set_title(f"Solution for {dataset_name} {file_suffix}", fontsize=16, pad=20)

    plt.savefig(os.path.join(os.path.dirname(solution_path), f"{dataset_name}_highlighted{file_suffix}.svg"))
    plt.show()

    # Create a second plot zooming in on the highlighted area
    highlighted_bounds = subdivision[subdivision["highlight"]].geometry.total_bounds
    zoom_ax = subdivision.plot(
        linewidth=1,
        edgecolor="grey",
        facecolor=subdivision["highlight"].map({True: highlight_color, False: base_color}),
    )
    zoom_ax.set_xlim(highlighted_bounds[0], highlighted_bounds[2])
    zoom_ax.set_ylim(highlighted_bounds[1], highlighted_bounds[3])
    zoom_ax.axis("off")
    zoom_ax.set_title(f"Zoomed-In Solution for {dataset_name} {file_suffix}", fontsize=16, pad=20)

    plt.savefig(os.path.join(os.path.dirname(solution_path), f"{dataset_name}_highlighted_zoomed{file_suffix}.svg"))
    plt.show()


if __name__ == '__main__':

    datasets = ["avignon", "braunschweig", "issoire", "karlsruhe", "neumuenster","rheinruhr"]
    for dataset_name in datasets:
        plot_shapefile_with_highlights(dataset_name)