import pytest
from osgeo import osr

from network_analysis.population_data import (
    open_and_reproject_raster,
    get_node_coordinates,
    get_population_at_nodes,
    select_nodes_by_population_weight,
    get_population_weighted_nodes,
)


def test_open_and_reproject_raster(temp_raster_file):
    # Test opening and re-projecting of a raster
    raster_dataset = open_and_reproject_raster(temp_raster_file)
    assert raster_dataset is not None
    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(4326)
    assert raster_dataset.GetProjectionRef() == target_srs.ExportToWkt()
    assert raster_dataset.GetRasterBand(1).ReadAsArray(1, 1, 1, 1)[0, 0] == 4.0


def test_get_node_coordinates(sample_nodes):
    # Test extracting coordinates from node data
    coordinates = get_node_coordinates(sample_nodes)
    assert len(coordinates) == len(sample_nodes)
    assert coordinates[1] == (88.7, -179.1)
    assert coordinates[2] == (88.8, -178.9)


def test_get_population_at_nodes(temp_raster_file, sample_nodes):
    # Test getting population values at nodes
    raster_dataset = open_and_reproject_raster(temp_raster_file)
    node_coordinates = get_node_coordinates(sample_nodes)
    population_values = get_population_at_nodes(raster_dataset, node_coordinates)
    assert len(population_values) == len(sample_nodes)
    assert population_values == [3.0, 4.0]


def test_select_nodes_by_population_weight(temp_raster_file, sample_nodes):
    # Test selecting nodes by population weight
    raster_dataset = open_and_reproject_raster(temp_raster_file)
    node_coordinates = get_node_coordinates(sample_nodes)
    population_values = get_population_at_nodes(raster_dataset, node_coordinates)
    start_nodes, end_nodes = select_nodes_by_population_weight(
        node_coordinates, population_values, num_nodes_to_select=2
    )
    assert len(start_nodes) == 2
    assert len(end_nodes) == 2


def test_get_population_weighted_nodes_no_population(sample_nodes):
    # Test getting population-weighted nodes
    start_nodes, end_nodes = get_population_weighted_nodes(sample_nodes, 2)
    assert len(start_nodes) == 2
    assert len(end_nodes) == 2


def test_get_population_weighted_nodes_with_population(nodes_heidelberg):
    # Test getting population-weighted nodes
    start_nodes, end_nodes = get_population_weighted_nodes(nodes_heidelberg, 2)
    assert len(start_nodes) == 2
    assert len(end_nodes) == 2


if __name__ == "__main__":
    pytest.main()
