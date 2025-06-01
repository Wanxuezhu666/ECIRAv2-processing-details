
"""
Updated: Wanxue Zhu (wanxue.zhu@agr.uni-goettingen.de)
Date: 2025-June-01
"""

"""
This code is used to generate the NUTS code for each grid. 
The NUTS codes are replaced by numbers, 
and the specific correspondence between each number and the NUTS2 unit can be found in the xlsx file:
"NUTS_number_list_new.xlsx".

"""

import numpy as np
import geopandas as gpd
import rasterio
from shapely.geometry import Point
from tqdm import tqdm

def assign_nuts_to_raster(boundary_shapefile, raster_file, output_raster):
    boundary = gpd.read_file(boundary_shapefile)  
    with rasterio.open(raster_file) as src:
        transform = src.transform
        crs = src.crs
        data = src.read(1)
        nodata_value = src.nodata if src.nodata is not None else -1
        nuts_codes = np.full(data.shape, 0, dtype=np.uint16)  # 初始化为0
        rows, cols = data.shape
        x_coords, y_coords = np.meshgrid(np.arange(cols) + 0.5, np.arange(rows) + 0.5)
        x_coords, y_coords = rasterio.transform.xy(transform, y_coords, x_coords)
        x_coords = np.array(x_coords)
        y_coords = np.array(y_coords)
        # Transfer point list to GeoDataFrame
        points = gpd.GeoDataFrame(geometry=gpd.points_from_xy(x_coords.flatten(), y_coords.flatten()), crs=crs)
        # Connect points with polygon
        joined = gpd.sjoin(points, boundary, how='left', op='within')
        nuts_codes = joined['ID'].fillna(0).values.reshape(data.shape).astype(np.uint16)
        # Save data
        out_meta = src.meta.copy()
        out_meta.update({"dtype": "uint16", "nodata": 0})
        with rasterio.open(output_raster, 'w', **out_meta) as dst:
            dst.write(nuts_codes, 1)

# 示例用法
assign_nuts_to_raster(
    'D:/02_CRC_project/13_Grid_crop_specific_AAI/11_Zonal_calibration/NUS2010_NUTS2_01m_3035.shp',
    'E:/01_Reseach_papers/FA_Pre_irrigation_grid_map/Depository/Input_01_PCTM/UAA_2010_2020_revised_100/UAA_2010.tif',
    'E:/01_Reseach_papers/FA_Pre_irrigation_grid_map/Depository/Input_01_PCTMGrid_ID_22.tif'
)









