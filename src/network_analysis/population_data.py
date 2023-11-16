import random
import logging as log

from osgeo import gdal, osr
from typing import List, Dict, Tuple, Union

from definitions import CRS_EPSG_4326, RASTER_PATH


def open_and_reproject_raster(raster_path: str) -> Union[gdal.Dataset, None]:
    """
    Open and if CRS is not EPSG 4326 reproject a raster dataset to EPSG 4326 (WGS 84).

    Args:
        raster_path (str): Path to the input raster dataset.

    Returns:
        gdal.Dataset or None: Reprojected raster dataset.
    """
    try:
        # Open the input raster dataset
        raster_dataset = gdal.Open(raster_path)
        if raster_dataset is None:
            log.error("Failed to open the raster dataset.")
            raise Exception("Failed to open the raster dataset.")

        # Get the spatial reference of the input raster
        raster_srs = osr.SpatialReference(wkt=raster_dataset.GetProjection())

        # Check if the input raster is already in EPSG 4326, else reproject
        if raster_srs.GetAttrValue("AUTHORITY", 1) != str(CRS_EPSG_4326):
            log.warning(
                "The input raster data does not have CRS 4326."
                " Re-projecting to CRS 4326."
            )
            raster_dataset = gdal.Warp(
                raster_path, raster_path, format="GTiff", dstSRS="EPSG:4326"
            )
        return raster_dataset

    except Exception as e:
        log.error(f"Error opening and re-projecting raster: {e}")
        raise e


def get_node_coordinates(
    nodes: Dict[int, Dict[str, float]]
) -> Dict[int, Tuple[float, float]]:
    """
    Get the coordinates of nodes from a network graph.

    Args:
        nodes (dict): A dictionary of nodes with OSM IDs and coordinate data.

    Returns:
        dict: A dictionary with OSM IDs as keys and (latitude, longitude)
         coordinates as values.
    """
    return {osm_id: (data["y"], data["x"]) for osm_id, data in nodes.items()}


def get_population_at_nodes(
    raster_dataset: gdal.Dataset, nodes: Dict[int, Tuple[float, float]]
) -> List[float]:
    """
    Get population values at nodes by sampling from a reprojected raster dataset.

    Args:
        raster_dataset (gdal.Dataset): Reprojected raster dataset.
        nodes (dict): Dictionary of node coordinates.

    Returns:
        list: A list of population values corresponding to each node.
    """
    geotransform = raster_dataset.GetGeoTransform()
    origin_x = geotransform[0]
    origin_y = geotransform[3]
    pixel_width = geotransform[1]
    pixel_height = geotransform[5]

    population_at_nodes = []

    # get population values at nodes
    for osm_id, (y, x) in nodes.items():
        raster_x = int((x - origin_x) / pixel_width)
        raster_y = int((y - origin_y) / pixel_height)

        raster_band = raster_dataset.GetRasterBand(1)
        pixel_value = raster_band.ReadAsArray(raster_x, raster_y, 1, 1)[0][0]

        population_at_nodes.append(pixel_value)

    return population_at_nodes


def select_nodes_by_population_weight(
    nodes: Dict[int, Tuple[float, float]],
    population_weights: List[float],
    num_nodes_to_select: int,
) -> Tuple[List[int], List[int]]:
    """
    Get a pair of start and end nodes weighted by population.

    Args:
        nodes (dict): Dictionary of node coordinates.
        population_weights (list): List of population values at nodes.
        num_nodes_to_select (int): Number of nodes to select.

    Returns:
        tuple: Two lists containing the selected start and end nodes.
    """
    if sum(population_weights) == 0:
        log.warning(
            "The sum of population weights is 0. "
            "Cannot select nodes. Using random selection."
        )
        start_nodes = random.choices(list(nodes), k=num_nodes_to_select)

        end_nodes = random.choices(list(nodes), k=num_nodes_to_select)
    # TODO: check that start and end node at the same index are not the same
    else:
        start_nodes = random.choices(
            list(nodes), weights=population_weights, k=num_nodes_to_select
        )

        end_nodes = random.choices(
            list(nodes), weights=population_weights, k=num_nodes_to_select
        )
    return start_nodes, end_nodes


def get_population_weighted_nodes(
    nodes: Dict[int, Dict[str, float]],
    num_nodes_to_select: int,
) -> Tuple[List[int], List[int]]:
    """
    Get a pair of start and end nodes weighted by population.

    Args:
        nodes (dict): Dictionary of node coordinates.
        num_nodes_to_select (int): Number of nodes to select.

    Returns:
        tuple: Two lists containing the selected start and end nodes.
    """
    try:
        absolute_path = RASTER_PATH
        raster_dataset = open_and_reproject_raster(absolute_path)
        if raster_dataset is None:
            log.error("Failed to access the raster dataset.")
            raise Exception("Failed to access the raster dataset.")
        node_coordinates = get_node_coordinates(nodes)
        population_at_nodes = get_population_at_nodes(raster_dataset, node_coordinates)
        start_nodes, end_nodes = select_nodes_by_population_weight(
            node_coordinates, population_at_nodes, num_nodes_to_select
        )
        return start_nodes, end_nodes

    except Exception as e:
        log.error(f"Error in get_population_weighted_nodes: {e}")
        raise e
