import os

# get root directory
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

# get data directory
DATA_DIR = os.path.join(ROOT_DIR, "data")

# get raster data directory
RASTER_PATH = os.path.join(DATA_DIR, "ghspop_4326.tif")

# get test data directory
TEST_DATA_DIR = os.path.join(ROOT_DIR, "tests", "test_data")

CRS_EPSG_4326 = 4326
