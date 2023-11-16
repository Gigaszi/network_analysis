import re

import geopandas as gpd
import matplotlib.pyplot as plt

import networkx as nx
import osmnx as ox
import pandas as pd

import argparse
import logging as log
import os
import sys
from argparse import Namespace


def save_centrality_results(centrality_gdf, output_folder) -> None:
    """
    Save centrality results to a GeoPackage file.

    Args:
        centrality_gdf (geopandas.GeoDataFrame): GeoDataFrame containing
         centrality data.
        output_folder (str): The folder where results will be saved.
    """
    log.info("Save output to GeoPackage.")
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        output_filepath = os.path.join(output_folder, "centrality_results.gpkg")
        centrality_gdf.to_file(output_filepath, driver="GPKG", index=False)

        log.info(f"Centrality results saved to: {output_filepath}")
    except Exception as e:
        log.error(f"An error occurred while saving centrality results: {e}")


def parse_arguments() -> Namespace:
    """
    Parse command-line arguments for the network analysis.

    Returns:
        Namespace: The configured argument namespace.
    """
    parser = argparse.ArgumentParser(
        description="Calculate centrality for a study area."
    )
    parser.add_argument(
        "-l",
        "--location",
        type=str,
        nargs="?",
        default="Heidelberg, Germany",
        help="Study area, e.g., 'Heidelberg, Germany'"
        " (default: 'Heidelberg, Germany')",
    )
    parser.add_argument(
        "-m",
        "--centrality_method",
        type=str,
        choices=["networkx", "geographical"],
        default="networkx",
        help="Method to calculate centrality "
        "(networkx or geographical, default: networkx)",
    )
    parser.add_argument(
        "-n",
        "--num_routes",
        type=int,
        help="Number of routes (only for the networkx method)",
    )
    parser.add_argument(
        "-r",
        "--route_type",
        type=str,
        choices=["length", "travel_time"],
        default="length",
        help="Route type for which the betweeness centrality will be calculated, (default: length)",
    )
    parser.add_argument(
        "-o",
        "--output_folder",
        type=str,
        default="output_results",
        nargs="?",
        help="Output folder for results (default: output_results)",
    )
    parser.add_argument(
        "-t",
        "--network_type",
        type=str,
        choices=["all_private", "all", "bike", "drive", "drive_service", "walk"],
        default="drive",
        help="Type of street network (default: drive)",
    )
    parser.add_argument(
        "-w",
        "--weighting",
        type=str,
        choices=["random", "population"],
        help="Weighting method for geographical centrality (default: random)",
    )
    args = parser.parse_args()

    if args.centrality_method == "geographical":
        if args.num_routes is None:
            log.error("Number of routes must be specified for geographical analysis.")
            sys.exit(1)
        if args.num_routes <= 0:
            log.error("Number of routes must be a positive integer.")
            sys.exit(1)
    if args.centrality_method == "networkx":
        if args.num_routes:
            log.warning("Networkx method does not support a number of routes.")
        if args.weighting:
            log.warning("Networkx method does not support a weighting method.")

    return args


def get_osm_graph(location: str, network_type: str) -> nx.Graph:
    """
    Retrieves a street network graph for a given location and network type
    based on OpenStreetMap.

    Args:
        location (str): The location (place name) for which to fetch the graph.
        network_type (str): The type of network data to retrieve
        ("all_private", "all", "bike", "drive", "drive_service", "walk").

    Returns:
        networkx.Graph: The OpenStreetMap graph.
    """
    try:
        return ox.graph_from_place(location, network_type=network_type, simplify=True)
    except ox._errors.InsufficientResponseError as e:
        log.error(
            f"Place not found: '{location}'. Please check the spelling and try again."
        )
        raise e
    except Exception as e:
        log.error(
            f"An unexpected error occurred while creating a graph from location: {e}"
        )
        raise e


def create_centrality_geodataframe(centrality_df, graph) -> gpd.GeoDataFrame:
    """
    Creates a GeoDataFrame with centrality information based on a DataFrame
     and a street network graph.

    Args:
        centrality_df (pandas.DataFrame): DataFrame containing centrality information.
        graph (networkx.Graph): Street network graph.

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame with centrality information.
    """
    centrality_df.columns = ["u", "v", "key", "centrality"]
    centrality_df = centrality_df.set_index(["u", "v", "key"])
    nodes_df, edges_df = ox.graph_to_gdfs(graph)
    centrality_gdf = centrality_df.join(edges_df[["osmid", "geometry"]])
    centrality_gdf = gpd.GeoDataFrame(centrality_gdf, crs=4326)
    centrality_gdf["osmid"] = centrality_gdf["osmid"].astype(str)
    return centrality_gdf


def plot_road_network(
    geodataframe, output_folder, column="centrality", cmap="magma_r"
) -> None:
    """
    Plots the road network and saves the plot to an output folder.

    Args:
        geodataframe (geopandas.GeoDataFrame): GeoDataFrame with road network data.
        output_folder (str): Path to the folder where the plot should be saved.
        column (str, optional): The column to use for coloring the plot.
         Defaults to "centrality".
        cmap (str, optional): The colormap to use for coloring the plot.
         Defaults to "magma_r".
    """
    log.info("Creating output plot.")
    try:
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        fig, ax = plt.subplots(figsize=(10, 10))
        geodataframe.plot(column=column, cmap=cmap, ax=ax, legend=True)
        plt.title("Road Network Centrality")
        plt.xlabel("Longitude")
        plt.ylabel("Latitude")

        output_filepath = os.path.join(
            output_folder, "road_network_centrality_plot.png"
        )
        plt.savefig(output_filepath, dpi=300, bbox_inches="tight")
        plt.close()

        log.info(f"Plot saved to: {output_filepath}")

    except Exception as e:
        log.info(f"An error occurred in the plot creation: {e}")


# Dictionary of speed limits for different road types.
speed_limits = {
    "drive": {
        "motorway": 100,
        "motorway_link": 60,
        "motorroad": 90,
        "trunk": 85,
        "trunk_link": 60,
        "primary": 65,
        "primary_link": 50,
        "secondary": 60,
        "secondary_link": 50,
        "tertiary": 50,
        "tertiary_link": 40,
        "unclassified": 30,
        "residential": 30,
        "living_street": 10,
        "service": 20,
        "road": 20,
        "track": 15,
        "path": None,
        "footway": None,
        "pedestrian": None,
        "cycleway": None,
    },
    "bike": {
        "motorway": None,
        "motorway_link": None,
        "motorroad": None,
        "trunk": 18,
        "trunk_link": 18,
        "primary": 18,
        "primary_link": 18,
        "secondary": 18,
        "secondary_link": 18,
        "tertiary": 18,
        "tertiary_link": 18,
        "unclassified": 16,
        "residential": 18,
        "living_street": 6,
        "service": 14,
        "road": 12,
        "track": 12,
        "path": 12,
        "footway": 6,
        "pedestrian": 6,
        "cycleway": 18,
    },
}


def calculate_route(graph, route_type, network_type) -> pd.DataFrame:
    """
    Calculates centrality metrics for a given graph based on the selected route type.

    Args:
        graph (networkx.Graph): Street network graph.
        route_type (str): The type of route for centrality calculation.
        network_type (str, optional): The network type for speed limit information.

    Returns:
        pandas.DataFrame: DataFrame containing centrality values.
    """
    if route_type == "travel_time":
        graph = add_travel_time(graph, network_type)
    betweenness_centrality = nx.edge_betweenness_centrality(graph, weight=route_type)
    centrality_df = pd.DataFrame(
        index=betweenness_centrality.keys(),
        data=betweenness_centrality.values(),
    )
    return centrality_df


def add_travel_time(graph, network_type) -> nx.Graph:
    """
    Adds travel time information to the graph based on speed limits.

    Args:
        graph (networkx.Graph): Street network graph.
        network_type (str): The network type for speed limit information.

    Returns:
        networkx.Graph: Graph with added travel time information.
    """
    try:
        hwy_speeds = speed_limits[network_type]
    except KeyError:
        log.error(
            f"Speeds for {network_type} not implemented yet."
            f" Please choose one of the following: {speed_limits.keys()}"
        )
        raise KeyError
    graph = ox.add_edge_speeds(graph, hwy_speeds)
    graph = ox.add_edge_travel_times(graph)

    return graph


def create_output_folder(
    output_path: str,
    location: str,
    centrality_method: str,
    route_type: str,
) -> str:
    """
    Create an output folder for saving analysis results.

    Args:
        output_path (str): The base path for the output folder.
        location (str): The location or study area name.
        centrality_method (str): The method used for centrality analysis.
        route_type (str): The type of route for analysis.

    Returns:
        str: The path to the created output folder.
    """
    folder_name = location + "_" + centrality_method + "_" + route_type
    folder_name = re.sub(r"[^a-zA-Z0-9]+", "_", folder_name)

    folder_path = os.path.join(output_path, folder_name)

    if os.path.isdir(folder_path):
        # If it exists, delete it
        try:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    os.remove(os.path.join(root, file))
            os.rmdir(folder_path)
        except OSError as e:
            log.error(f"Error deleting folder '{folder_path}': {e}")

    try:
        os.makedirs(folder_path)
        log.info(f"Your results will be saved to {folder_path}")
    except OSError as e:
        log.error(f"Error creating folder '{folder_path}': {e}")
    return folder_path
