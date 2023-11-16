# Network Analysis

## Overview

Welcome to the **Network Analysis** project! This Python project is designed for analyzing and visualizing the betweeness centrality of road networks using various tools and libraries.

## Installation

To set up the project, follow the steps below for a hassle-free installation. This project utilizes Python and Anaconda for environment management

### Prerequisites

Before you begin, ensure that you have Python and Anaconda installed on your system. If not, you can download and install Anaconda from Anaconda's official website.

#### Installation Steps

Clone the Repository:

```bash
git clone https://courses.gistools.geog.uni-heidelberg.de/mh220/05_network_analysis.git
cd 05_network_analysis
```

Create and Activate Conda Environment:

```bash
conda env create -f environment.yml
conda activate network_analysis
```
Now, your environment is configured, and you're ready to run and contribute to the project!

#### Raster Data

The project requires raster data for the population-weighted geographical centrality analysis. In this project the [GHS population grid](https://ghsl.jrc.ec.europa.eu/ghs_pop2023.php) is used. The data is available on the [here](https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/GHS_POP_GLOBE_R2023A/GHS_POP_E2030_GLOBE_R2023A_4326_3ss/V1-0/GHS_POP_E2030_GLOBE_R2023A_4326_3ss_V1_0.zip). Download the data and place it in the `data` folder as `ghspop_4326.tif`.

## Usage

The project is called via the CLI, navigate to the `src` directory and run the following command:

```bash
cd src
python main.py -l "Heidelberg, Germany" -m "networkx" -n 5 -r "length" -o "output_results" -t "drive"
```

The following parameters are available:

| Parameter              | Short Option | Long Option         | Type   | Choices                                 | Default Value         | Description                               |
|------------------------|--------------|---------------------|--------|----------------------------------------|-----------------------|-------------------------------------------|
| Study Area Location    | -l           | --location          | String |                                        | "Dossenheim, Germany" | Study area, e.g., 'Heidelberg, Germany' (default: 'Dossenheim, Germany') |
| Centrality Method      | -m           | --centrality_method | String | "networkx" or "geographical"            | "networkx"            | Method to calculate centrality (default: networkx) |
| Number of Routes      | -n           | --num_outes         | Int    |                                        | -                     | Number of routes (only for the networkx method) |
| Route Type             | -r           | --route_type        | String | "length" or "travel_time"              | "length"              | Route type, optional, default: length     |
| Output Folder          | -o           | --output_folder     | String |                                        | "output_results"      | Output folder for results (default: output_results) |
| Network Type           | -t           | --network_type      | String | "all_private", "all", "bike", "drive", "drive_service", "walk" | "drive"               | Type of street network (default: drive) |
| Weighting Method       | -w           | --weighting         | String | "random" or "population"              | -                     | Weighting method for geographical centrality (default: random) |


## Dependencies

- [Python](https://www.python.org/) (>=3.10)
- [NetworkX](https://networkx.github.io/) (>=3.1)
- [pytest](https://pytest.org/) (>=7.4.0)
- [OSMnx](https://osmnx.readthedocs.io/) (>=1.6.0)
- [Matplotlib](https://matplotlib.org/) (>=3.7.2)
- [Jupyter](https://jupyter.org/) (>=1.0.0)
- [Mock](https://docs.python.org/3/library/unittest.mock.html) (>=5.1.0)
- [GeoPandas](https://geopandas.org/) (>=0.10.2)

## Contribution

If you find any issues or have suggestions for improvements, feel free to open an issue or submit a pull request. Contributions are welcome!

---

Enjoy exploring and analyzing networks with the **Network Analysis** project!

## Example

Calculate the betweenness centrality for the study area Heidelberg, Germany for the shortest paths for all roads accessible with the car.
```bash
cd src
python main.py -l "Heidelberg, Germany" -m "networkx" -r "length" -o "output_results" -t "drive"
```

Calculate the betweenness centrality for the study area Heidelberg, Germany for the shortest travel time for 5 random selected paths for all roads accessible with the car.
```bash
cd src
python main.py -l "Heidelberg, Germany" -m "geographical" -n 5 -r "travel_time" -o "output_results" -t "drive" -w "random"
```

Calculate the betweenness centrality for the study area Heidelberg, Germany for the shortest path for 5 paths selected based on the population for all roads accessible with a bike.
```bash
cd src
python main.py -l "Heidelberg, Germany" -m "geographical" -n 5 -r "length" -o "output_results" -t "bike" -w "population"
```