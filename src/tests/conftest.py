import os

import numpy as np
import pytest
import geopandas as gpd
import osmnx as ox
import pandas as pd
from osgeo import gdal, osr
from definitions import TEST_DATA_DIR


@pytest.fixture(scope="session")
def tmp_output_folder(tmp_path_factory):
    return tmp_path_factory.mktemp("output")


@pytest.fixture(scope="session")
def get_test_gdf():
    path = os.path.join(TEST_DATA_DIR, "test_dataframe.gpkg")
    return gpd.read_file(path)


@pytest.fixture
def test_graph():
    return ox.graph_from_place("Dossenheim, Germany", network_type="drive")


@pytest.fixture
def test_centrality_df():
    return pd.DataFrame(
        [
            {"u": "123", "v": "456", "key": 0, "to_be_centrality": 1},
            {"u": "234", "v": "567", "key": 0, "to_be_centrality": 1},
            {"u": "345", "v": "678", "key": 0, "to_be_centrality": 1},
        ]
    )


@pytest.fixture(scope="session")
def sample_nodes():
    return {
        1: {"x": -179.1, "y": 88.7},
        2: {"x": -178.9, "y": 88.8},
    }


@pytest.fixture(scope="session")
def nodes_heidelberg():
    return {
        1: {"x": 8.6349536, "y": 49.4115105},
        2: {"x": 8.6342228, "y": 49.4237764},
    }


@pytest.fixture(scope="session")
def temp_raster_file(tmp_output_folder):
    temp_raster_path = os.path.join(tmp_output_folder, "temp_raster.tif")
    ds = gdal.GetDriverByName("GTiff").Create(
        temp_raster_path, 2, 2, 1, gdal.GDT_Float32
    )

    ds.SetGeoTransform((-180, 1, 0, 90, 0, -1))
    ds.GetRasterBand(1).WriteArray(np.array([[1.0, 2.0], [3.0, 4.0]]))
    target_srs = osr.SpatialReference()
    target_srs.ImportFromEPSG(4324)
    ds.SetProjection(target_srs.ExportToWkt())

    ds.FlushCache()
    ds = None
    return temp_raster_path
