import network_analysis.osmnx_analyser as osmnx_analyser
import pytest


def test_osmnx_analyser_random_weighting_return():
    result = osmnx_analyser.osmnx_analyser(
        "Heidelberg, Germany", 5, "length", "drive", "random"
    )
    assert result is not None


def test_osmnx_analyser_parameter_validation():
    with pytest.raises(ValueError):
        osmnx_analyser.osmnx_analyser(
            "Heidelberg, Germany", 5, "route_type", "network_type", "invalid_weighting"
        )


def test_osmnx_analyser_population_weighting():
    result = osmnx_analyser.osmnx_analyser(
        "Heidelberg, Germany", 5, "length", "drive", "population"
    )
    assert result is not None


if __name__ == "__main__":
    pytest.main()
