import random

import networkx as nx
import osmnx as ox
import pandas as pd
import logging as log

from network_analysis.population_data import get_population_weighted_nodes
from network_analysis.utils import (
    get_osm_graph,
    create_centrality_geodataframe,
    add_travel_time,
)


def osmnx_analyser(
    location: str, num_routes: int, route_type: str, network_type: str, weighting: str
) -> pd.DataFrame:
    log.info(
        f"Start geographical betweenness centrality analysis for {num_routes} routes."
    )

    graph = get_osm_graph(location=location, network_type=network_type)

    # get start and end nodes for routes depending on weighting method
    if weighting == "population":
        start_nodes, end_nodes = get_population_weighted_nodes(graph.nodes, num_routes)
    elif weighting == "random":
        start_nodes = [random.choice(list(graph.nodes)) for _ in range(num_routes)]
        end_nodes = [random.choice(list(graph.nodes)) for _ in range(num_routes)]
    else:
        log.error("Invalid weighting method specified.")
        raise ValueError("Invalid weighting method specified.")

    if route_type == "travel_time":
        graph = add_travel_time(graph, network_type)

    routes_df = []
    # calculate routes for each start and end node pair
    for origin_node, destination_node in zip(start_nodes, end_nodes):
        try:
            route = ox.shortest_path(
                graph, origin_node, destination_node, weight=route_type, cpus=None
            )

            route_gdf = ox.utils_graph.route_to_gdf(graph, route)
            routes_df.append(route_gdf)
        # needed because of outgoing directed edges
        except nx.NetworkXNoPath:
            continue
        except Exception as e:
            if (
                "'NoneType' is not subscriptable" in str(e)
                or "'NoneType' object object is not subscriptable" in str(e)
                or "'NoneType' object is not subscriptable" in str(e)
                or "graph contains no edges" in str(e)
            ):
                continue
            else:
                log.error(f"An error occurred: {e}")
                raise e

    log.info(f"Created {len(routes_df)} routes.")
    route_gdf = pd.concat(routes_df, axis=0)

    centrality_series = route_gdf.groupby(["u", "v", "key"]).size()
    centrality_df = centrality_series.reset_index()

    return create_centrality_geodataframe(centrality_df, graph)
