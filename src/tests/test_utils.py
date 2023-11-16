import os

import pytest
import networkx as nx
import geopandas as gpd
import pandas as pd
from network_analysis.utils import (
    get_osm_graph,
    create_centrality_geodataframe,
    calculate_route,
    add_travel_time,
    speed_limits,
    plot_road_network,
)
import osmnx as ox


def test_get_osm_graph():
    # Test if the function returns a networkx graph
    location = "Dossenheim, Germany"
    network_type = "drive"
    graph = get_osm_graph(location, network_type)
    assert isinstance(graph, nx.Graph)
    assert len(graph.nodes) > 0
    assert len(graph.edges) > 0


def test_create_centrality_geodataframe(test_centrality_df, test_graph):
    # Test if the function returns a not empty GeoDataFrame
    geodataframe = create_centrality_geodataframe(test_centrality_df, test_graph)
    assert isinstance(geodataframe, gpd.GeoDataFrame)
    assert len(geodataframe) > 0


def test_calculate_route(test_graph):
    # Test if the function returns a not empty DataFrame
    route_type = "travel_time"
    network_type = "drive"
    centrality_df = calculate_route(test_graph, route_type, network_type)
    assert isinstance(centrality_df, pd.DataFrame)
    assert len(centrality_df) > 0


def test_add_travel_times(test_graph):
    # Test if the function returns a not empty graph and if
    # the correct columns are added
    network_types = ["all_private", "all", "bike", "drive", "drive_service", "walk"]
    for network_type in network_types:
        if network_type not in speed_limits.keys():
            with pytest.raises(KeyError):
                add_travel_time(test_graph, network_type)
        else:
            graph = add_travel_time(test_graph, network_type)
            assert isinstance(graph, nx.Graph)
            nodes_df, edges_df = ox.graph_to_gdfs(graph)
            assert "travel_time" in edges_df.columns
            assert "speed_kph" in edges_df.columns


def test_plot_road_network(get_test_gdf, tmp_output_folder):
    # Test if the function saves a plot in the output folder
    output_folder = str(tmp_output_folder)

    plot_road_network(get_test_gdf, output_folder)

    output_file = os.path.join(output_folder, "road_network_centrality_plot.png")
    assert os.path.exists(output_file)


if __name__ == "__main__":
    pytest.main()
