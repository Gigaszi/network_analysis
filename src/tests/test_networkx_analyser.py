import pytest
import geopandas as gpd
from network_analysis.networkx_analyser import networkx_analyser


def test_networkx_analyser_return():
    # Test if the function returns a GeoDataFrame and the expected columns
    result = networkx_analyser("Dossenheim, Germany", "length", "drive")
    assert isinstance(result, gpd.GeoDataFrame)

    assert "osmid" in result.columns
    assert "geometry" in result.columns
    assert "centrality" in result.columns


def test_networkx_analyser_parameter_validation():
    # Test parameter validation for input parameters
    with pytest.raises(ValueError):
        networkx_analyser("location", "invalid_route_type", "network_type")


if __name__ == "__main__":
    pytest.main()
