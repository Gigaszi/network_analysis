import logging as log
import geopandas as gpd
from network_analysis.utils import (
    get_osm_graph,
    create_centrality_geodataframe,
    calculate_route,
)


def networkx_analyser(
    location: str, route_type: str, network_type: str
) -> gpd.GeoDataFrame:
    """
    Analyze network centrality using NetworkX library.

    Args:
        location (str): The location or area for which to analyze centrality.
        route_type (str): The type of route for centrality calculation.
        network_type (str): The network type for routing and graph generation.

    Returns:
        geopandas.GeoDataFrame: GeoDataFrame containing centrality data.
    """
    log.info("Start NetworkX betweenness centrality analysis for the whole network.")

    graph = get_osm_graph(location=location, network_type=network_type)

    centrality_df = calculate_route(graph, route_type, network_type)

    # Reset index and create a GeoDataFrame with centrality information
    centrality_df.reset_index(inplace=True)
    centrality_gdf = create_centrality_geodataframe(centrality_df, graph)

    return centrality_gdf
