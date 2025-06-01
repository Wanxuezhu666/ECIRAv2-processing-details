"""
Updated: Wanxue Zhu (wanxue.zhu@agr.uni-goettingen.de)
Date: 2025-June-01

"""


import os
from osgeo import gdal


os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_03") 

# 3.4. Resampling GMIA 2005 from 0.01 arc degree (about 1.11 km at the equator) to 1km
# Note that no data for Cyprus
#================================================================================

def resample_tif(input_tif_a, input_tif_b, output_tif):
    a_dataset = gdal.Open(input_tif_a, gdal.GA_ReadOnly)
    b_dataset = gdal.Open(input_tif_b, gdal.GA_ReadOnly)
    a_projection = a_dataset.GetProjection()
    a_geotransform = a_dataset.GetGeoTransform()
    a_band = a_dataset.GetRasterBand(1)
    a_data_type = a_band.DataType
    b_projection = b_dataset.GetProjection()
    b_geotransform = b_dataset.GetGeoTransform()
    driver = gdal.GetDriverByName('GTiff')
    resample_dataset = driver.Create(output_tif, b_dataset.RasterXSize, b_dataset.RasterYSize, 1, a_data_type)
    resample_dataset.SetProjection(b_projection)
    resample_dataset.SetGeoTransform(b_geotransform)
    gdal.ReprojectImage(a_dataset, resample_dataset, a_projection, b_projection, gdal.GRA_Bilinear)#样条插值
    #gdal.ReprojectImage(a_dataset, resample_dataset, a_projection, b_projection, gdal.GRA_NearestNeighbour)#最邻近插值
    a_dataset = None
    b_dataset = None
    resample_dataset = None


resample_tif('Input_01_AEI_share_2005_001_arc_degree.tif', 
	         'Input_03_Reference_1km.tif', 
	         'AEI_share_2005_1km.tif')


# 3.5 Convert the shapefile generated in step 3.3 (in QGIS) into a TIFF file. 
#     This will create the GMIA AEI 2005 5 arc min TIFF.
#================================================================================

import geopandas as gpd
import rasterio
from rasterio.transform import from_origin
from rasterio.features import rasterize
import numpy as np

def shapefile_to_geotiff(shapefile_path, output_raster_path, column_name, resolution_deg=0.083333):
    gdf = gpd.read_file(shapefile_path)
    bounds = gdf.total_bounds
    minx, miny, maxx, maxy = bounds
    pixel_size = resolution_deg
    width = int((maxx - minx) / pixel_size)
    height = int((maxy - miny) / pixel_size)
    transform = from_origin(minx, maxy, pixel_size, pixel_size)
    if column_name not in gdf.columns:
        raise ValueError(f"Column '{column_name}' not found in Shapefile.")
    values = gdf[column_name]
    raster_array = np.zeros((height, width), dtype=np.float32)
    raster_array = rasterize(
        ((geom, value) for geom, value in zip(gdf.geometry, values)),
        out_shape=raster_array.shape,
        transform=transform,
        fill=0,  # Background value
        dtype=np.float32
    )
    with rasterio.open(
        output_raster_path, 'w',
        driver='GTiff',
        height=raster_array.shape[0],
        width=raster_array.shape[1],
        count=1,
        dtype=raster_array.dtype,
        crs=gdf.crs,
        transform=transform
    ) as dst:
        dst.write(raster_array, 1)
    print(f"GeoTIFF save as {output_raster_path}")


shapefile_path = 'Grid_5_arc_min_AEI2005_mean.shp'
output_raster_path = 'AEI_share_2005_5_arc_min.tif'
column_name = '_mean'
shapefile_to_geotiff(shapefile_path, output_raster_path, column_name)



# 3.6. Calculate the coefficients at 5 arc min level
# coefficients = HID / GMIA
#================================================================================

from osgeo import gdal
import numpy as np

def divide_tif(input_tif_a, input_tif_b, output_tif, nodata_value=None):
    a_dataset = gdal.Open(input_tif_a, gdal.GA_ReadOnly)
    b_dataset = gdal.Open(input_tif_b, gdal.GA_ReadOnly)
    projection = a_dataset.GetProjection()
    geotransform = a_dataset.GetGeoTransform()
    a_band = a_dataset.GetRasterBand(1)
    b_band = b_dataset.GetRasterBand(1)
    a_data = a_band.ReadAsArray()
    b_data = b_band.ReadAsArray()
    data_type = a_band.DataType
    if nodata_value is None:
        nodata_value = a_band.GetNoDataValue()
    with np.errstate(divide='ignore', invalid='ignore'):
        result_data = np.where(b_data != 0, a_data / b_data, nodata_value)
    if nodata_value is not None:
        result_data[(a_data == nodata_value) | (b_data == nodata_value)] = nodata_value
    driver = gdal.GetDriverByName('GTiff')
    output_dataset = driver.Create(output_tif, a_dataset.RasterXSize, a_dataset.RasterYSize, 1, data_type)
    output_dataset.SetProjection(projection)
    output_dataset.SetGeoTransform(geotransform)
    output_band = output_dataset.GetRasterBand(1)
    output_band.WriteArray(result_data)
    if nodata_value is not None:
        output_band.SetNoDataValue(nodata_value)
    a_dataset = None
    b_dataset = None
    output_dataset = None

divide_tif('Input_02_AEI_share_2010_5_arc_min.tif', 
	       'AEI_share_2005_5_arc_min.tif', 
	       'Coefficients_5_arc_min.tif')

# Resampling to 1km


resample_tif('Coefficients_5_arc_min.tif', 
	         'Input_03_Reference_1km.tif', 
	         'Coefficients_1km.tif')


# 3.7. Multiplying coefficients and GMIA 2005 at 1 km level
#================================================================================
from osgeo import gdal
import numpy as np


def multiply_tif(input_tif_a, input_tif_b, output_tif, nodata_value=None):
    a_dataset = gdal.Open(input_tif_a, gdal.GA_ReadOnly)
    b_dataset = gdal.Open(input_tif_b, gdal.GA_ReadOnly)
    projection = a_dataset.GetProjection()
    geotransform = a_dataset.GetGeoTransform()
    a_band = a_dataset.GetRasterBand(1)
    b_band = b_dataset.GetRasterBand(1)
    a_data = a_band.ReadAsArray()
    b_data = b_band.ReadAsArray()
    data_type = gdal.GDT_Float32
    if nodata_value is None:
        nodata_value = a_band.GetNoDataValue()
    with np.errstate(invalid='ignore'):
        result_data = np.where((a_data != nodata_value) & (b_data != nodata_value), a_data * b_data, nodata_value)
    driver = gdal.GetDriverByName('GTiff')
    options = ['COMPRESS=LZW']
    output_dataset = driver.Create(output_tif, a_dataset.RasterXSize, a_dataset.RasterYSize, 1, data_type, options)
    output_dataset.SetProjection(projection)
    output_dataset.SetGeoTransform(geotransform)
    output_band = output_dataset.GetRasterBand(1)
    output_band.WriteArray(result_data)
    if nodata_value is not None:
        output_band.SetNoDataValue(nodata_value)
    a_dataset = None
    b_dataset = None
    output_dataset = None


multiply_tif('Coefficients_1km.tif', 
	         'AEI_share_2005_1km.tif', 
	         'AEI_share_2010_1km.tif')



# 3.8 Revise the maximum AEI as 100 hectare
#================================================================================

import os
import rasterio

def process_geotiff(input_path, output_path):
    with rasterio.open(input_path) as src:
        img_array = src.read(1)
        img_array[img_array > 100] = 100
        metadata = src.meta.copy()
        metadata.update(dtype=rasterio.float32)
        with rasterio.open(output_path, 'w', **metadata) as dst:
            dst.write(img_array, 1)

# Define the input and output paths for a single TIFF file
input_path = r'E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_03\AEI_share_2010_1km.tif'  # Replace with your file path
output_path = r'E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_03\AEI_share_2010_1km_max_100.tif'  # Replace with your output path

# Process the single TIFF file
process_geotiff(input_path, output_path)


# 3.9 Add data for Cyprus using AEI 2010 1km from the resampling of 5 arc min
#================================================================================

import rasterio
from rasterio.warp import reproject, Resampling
import numpy as np
import os

os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_03") 


def fill_A_with_B(tifA_path, tifB_path, output_path, nodata_A=None, nodata_B=None):
    with rasterio.open(tifA_path) as srcA:
        dataA = srcA.read(1)
        profile = srcA.profile.copy()
        if nodata_A is None:
            nodata_A = srcA.nodata
    with rasterio.open(tifB_path) as srcB:
        dataB = srcB.read(1)
        if nodata_B is None:
            nodata_B = srcB.nodata
    reprojected_B = np.full(dataA.shape, nodata_B if nodata_B is not None else 0, dtype=dataB.dtype)
    reproject(
        source=dataB,
        destination=reprojected_B,
        src_transform=srcB.transform,
        src_crs=srcB.crs,
        dst_transform=srcA.transform,
        dst_crs=srcA.crs,
        resampling=Resampling.nearest
    )
    if nodata_B is not None:
        mask_B_valid = reprojected_B != nodata_B
    else:
        mask_B_valid = reprojected_B != 0
    dataA[mask_B_valid] = reprojected_B[mask_B_valid]
    dataA = dataA.astype(np.float32)
    profile.update(dtype=rasterio.float32, compress='lzw', nodata=nodata_A)
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(dataA, 1)


fill_A_with_B("AEI_share_2010_1km_max_100.tif", "Cyprus_AEI_2010.tif", "AEI_share_2010_1km_revised_100.tif")

