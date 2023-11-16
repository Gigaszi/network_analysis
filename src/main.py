import sys
import time
import logging as log
from network_analysis.osmnx_analyser import osmnx_analyser
from network_analysis.utils import plot_road_network, create_output_folder
from network_analysis.utils import save_centrality_results, parse_arguments
from network_analysis.networkx_analyser import networkx_analyser


def main() -> None:
    """
    The main function that orchestrates the network analysis process.

    Parses command-line arguments, performs network analysis, and saves results.

    """
    # Configure logging
    log.basicConfig(
        level=log.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    st = time.time()  # Record the start time

    args = parse_arguments()  # Parse command-line arguments

    if args.centrality_method == "networkx":
        centrality_gdf = networkx_analyser(
            location=args.location,
            route_type=args.route_type,
            network_type=args.network_type,
        )
    elif args.centrality_method == "geographical":
        centrality_gdf = osmnx_analyser(
            location=args.location,
            num_routes=args.num_routes,
            network_type=args.network_type,
            weighting=args.weighting,
            route_type=args.route_type,
        )
    else:
        log.error("Invalid centrality method specified.")
        sys.exit(1)

    # Create the output folder based on user-defined parameters
    output_path = create_output_folder(
        output_path=args.output_folder,
        location=args.location,
        centrality_method=args.centrality_method,
        route_type=args.route_type,
    )

    # Plot the road network centrality and save the plot
    plot_road_network(
        centrality_gdf,
        column="centrality",
        cmap="magma_r",
        output_folder=output_path,
    )

    # Save centrality results
    save_centrality_results(centrality_gdf=centrality_gdf, output_folder=output_path)

    et = time.time()  # Record the end time

    log.info(f"Analysis finished successfully after {et-st} seconds.")


if __name__ == "__main__":
    main()
