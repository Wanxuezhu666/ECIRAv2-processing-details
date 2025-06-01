
"""
Updated: Wanxue Zhu (wanxue.zhu@agr.uni-goettingen.de)
Date: 2025-June-01

DGPCM layer values:
description of bands:
0 -     weight (ha x 10)
1 -     Apples and other Fruits (share x 1000)
2 -     Barley (share x 1000)
3 -     Citrus Fruits (share x 1000)
4 -     Durum Wheat (share x 1000)
5 -     Flowers and ornamental plants (share x 1000)
6 -     Permanent grassland and meadows (share x 1000)
7 -     Maize (grain and green/silo) (share x 1000)
8 -     Rapeseed and turnip (share x 1000)
9 -     Nurseries (share x 1000)
10 -    Oats (share x 1000)
11 -    Other cereals (share x 1000)
12 -    Other permanent crops (share x 1000)
13 -    Other forage plants (share x 1000)
14 -    Other industrial plants (share x 1000)
15 -    Olive Plantations (share x 1000)
16 -    Rice (share x 1000)
17 -    Potatoes (share x 1000)
18 -    Pulses (share x 1000)
19 -    Fodder roots and brassicas (share x 1000)
20 -    Rye (share x 1000)
21 -    Soya (share x 1000)
22 -    Sugar beets (share x 1000)
23 -    Sunflowers (share x 1000)
24 -    Common wheat and spelt (share x 1000)
25 -    Other oil-seed or fibre crops (share x 1000)
26 -    Tobacco (share x 1000)
27 -    Fresh vegetables, melons, strawberries (share x 1000)
28 -    Vineyards (share x 1000)
"""

# 4.1 - Separate different layers

# Since the DGPCM dataset contains 29 layers, 
# with Layer 0 representing UAA and Layers 1-28 representing crop shares, 
# we firstly separated them into individual layers
#================================================================================

import os
import glob
import rasterio
from rasterio.enums import Resampling

def extract_UAA_layer(input_folder, uaa_output_folder):
    os.makedirs(uaa_output_folder, exist_ok=True)
    for tif in glob.glob(os.path.join(input_folder, '*.tif')):
        year = next((y for y in map(str, range(2010, 2021)) if y in tif), None)
        if not year: continue
        with rasterio.open(tif) as src:
            band = src.read(1)
            out_path = os.path.join(uaa_output_folder, f"UAA_{year}.tif")
            with rasterio.open(out_path, 'w', driver='GTiff', height=band.shape[0], width=band.shape[1],
                               count=1, dtype=band.dtype, crs=src.crs, transform=src.transform, compress='lzw') as dst:
                dst.write(band, 1)
        print(f"processing {year}")


def extract_crop_share_layers(input_folder, crop_output_folder):
    os.makedirs(crop_output_folder, exist_ok=True)
    for tif in glob.glob(os.path.join(input_folder, '*.tif')):
        year = next((y for y in map(str, range(2010, 2021)) if y in tif), None)
        print(f"processing {year}")
        if not year: continue
        with rasterio.open(tif) as src:
            for i in range(2, src.count + 1):
                band = src.read(i)
                out_dir = os.path.join(crop_output_folder, year)
                os.makedirs(out_dir, exist_ok=True)
                out_path = os.path.join(out_dir, f"crop_share_{year}_layer_{i-1}.tif")
                with rasterio.open(out_path, 'w', driver='GTiff', height=band.shape[0], width=band.shape[1],
                                   count=1, dtype=band.dtype, crs=src.crs, transform=src.transform, compress='lzw') as dst:
                    dst.write(band, 1)


input_folder = 'E:/01_Reseach_papers/R1_irrigation_grid_map/Data/DGPCM'
uaa_output_folder = r'E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_04\UAA_2010_2020'

crop_output_folder = r'E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_04\Crop_share'

extract_UAA_layer(input_folder, uaa_output_folder)
extract_crop_share_layers(input_folder, crop_output_folder)


# 4.2 Revise the maximum UAA as 100 hectare
# This UAA is not the final UAA, we will update it after calculating total AAI
# The updated UAA = maximum (UAA, Total AAI)
#================================================================================
import os
import numpy as np
import rasterio
from rasterio.enums import Resampling

def process_geotiff(input_path, output_path):
    with rasterio.open(input_path) as src:
        img_array = src.read(1) 
        img_array[img_array > 1000] = 1000
        metadata = src.meta.copy()
        metadata.update(dtype=rasterio.uint16,compress='lzw')  
        with rasterio.open(output_path, 'w', **metadata) as dst:
            dst.write(img_array, 1)  

def process_all_geotiffs(input_folder, output_folder):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.tif') or filename.lower().endswith('.tiff'):
            input_path = os.path.join(input_folder, filename)
            output_path = os.path.join(output_folder, filename)
            process_geotiff(input_path, output_path)


input_folder = r'E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_04\UAA_2010_2020'  
output_folder = r'E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_04\UAA_2010_2020_revised_100'  

process_all_geotiffs(input_folder, output_folder)


# 4.3 Calculate UAA loss caused by revising the maximum UAA to 100 hectares (optional).
#================================================================================
#*********************************************************************************
import os
import numpy as np
import rasterio

def process_geotiff(input_path, output_path):
    with rasterio.open(input_path) as src:
        data = src.read(1)
        processed_data = np.where(data > 1000, data - 1000, 0)
        profile = src.profile
        profile.update(dtype=processed_data.dtype,compress='lzw')
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(processed_data, 1)

def traverse_and_process(input_directory, output_directory):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    for root, _, files in os.walk(input_directory):
        for file in files:
            if file.endswith('.tif') or file.endswith('.geotiff'):
                input_file = os.path.join(root, file)
                relative_path = os.path.relpath(root, input_directory)
                output_dir = os.path.join(output_directory, relative_path)
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                output_file = os.path.join(output_dir, f"processed_{file}")
                process_geotiff(input_file, output_file)
                print(f"Processed {input_file} -> {output_file}")


input_directory = r'E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_04\UAA_2010_2020'
output_directory = r'E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_04\UAA_2010_2020_loss'


traverse_and_process(input_directory, output_directory)

#*********************************************************************************

# 4.4 Aggregated some crop types to generate CERE and OTHER categories
#================================================================================

import numpy as np
import xlwt
import matplotlib.pyplot as plt
import xlrd
import math
import pandas as pd
import os
import seaborn as sns
import geopandas as gpd
from osgeo import gdal, ogr
import rasterio
from rasterio.mask import mask


os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_04") 

"""
CERE (layer 29) = soft wheat (layer 24) + durum wheat (4) + barley (2) + rye (20) + oats (10) + other cereals (11)
OTHER (layer 30) = ROOF + SOYA + TOBA + OIND + FLOW + OFAR + NURS + OCRO
      = 19 + 21 + 26 + 14 + 5 + 13 + 9 + 12

"""

# cereals excluding rice and maize

for num in range(11):
    year = num+2010
    input_files = [f'Crop_share/{year}/crop_share_{year}_layer_24.tif', 
                   f'Crop_share/{year}/crop_share_{year}_layer_4.tif', 
                   f'Crop_share/{year}/crop_share_{year}_layer_2.tif', 
                   f'Crop_share/{year}/crop_share_{year}_layer_20.tif', 
                   f'Crop_share/{year}/crop_share_{year}_layer_10.tif', 
                   f'Crop_share/{year}/crop_share_{year}_layer_11.tif']
    dataset = gdal.Open(input_files[0])
    proj = dataset.GetProjection()
    geo_transform = dataset.GetGeoTransform()
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    output_file = f'Crop_share/{year}/crop_share_{year}_layer_29.tif'
    driver = gdal.GetDriverByName('GTiff')
    creation_options = ['COMPRESS=LZW']
    output_dataset = driver.Create(output_file, cols, rows, 1, gdal.GDT_UInt16, creation_options)
    output_dataset.SetProjection(proj)
    output_dataset.SetGeoTransform(geo_transform)
    output_array_1 = None
    for input_file in input_files:
        dataset = gdal.Open(input_file)
        band_1 = dataset.GetRasterBand(1)
        array_1 = band_1.ReadAsArray()
        if output_array_1 is None:
            output_array_1 = array_1
        else:
            output_array_1 += array_1
    output_band_1 = output_dataset.GetRasterBand(1)
    output_band_1.WriteArray(output_array_1)
    output_dataset = None
    print(f'Done_year_{year}!')


#--------------------other crops------------

for num in range(11):
    year = num+2010
    input_files = [f'Crop_share/{year}/crop_share_{year}_layer_19.tif', 
                   f'Crop_share/{year}/crop_share_{year}_layer_21.tif', 
                   f'Crop_share/{year}/crop_share_{year}_layer_26.tif', 
                   f'Crop_share/{year}/crop_share_{year}_layer_14.tif', 
                   f'Crop_share/{year}/crop_share_{year}_layer_5.tif', 
                   f'Crop_share/{year}/crop_share_{year}_layer_13.tif', 
                   f'Crop_share/{year}/crop_share_{year}_layer_9.tif', 
                   f'Crop_share/{year}/crop_share_{year}_layer_12.tif']
    dataset = gdal.Open(input_files[0])
    proj = dataset.GetProjection()
    geo_transform = dataset.GetGeoTransform()
    cols = dataset.RasterXSize
    rows = dataset.RasterYSize
    output_file = f'Crop_share/{year}/crop_share_{year}_layer_30.tif'
    driver = gdal.GetDriverByName('GTiff')
    creation_options = ['COMPRESS=LZW']
    output_dataset = driver.Create(output_file, cols, rows, 1, gdal.GDT_UInt16, creation_options)
    output_dataset.SetProjection(proj)
    output_dataset.SetGeoTransform(geo_transform)
    output_array_1 = None
    for input_file in input_files:
        dataset = gdal.Open(input_file)
        band_1 = dataset.GetRasterBand(1)
        array_1 = band_1.ReadAsArray()
        if output_array_1 is None:
            output_array_1 = array_1
        else:
            output_array_1 += array_1
    output_band_1 = output_dataset.GetRasterBand(1)
    output_band_1.WriteArray(output_array_1)
    output_dataset = None
    print(f'Done_year_{year}!')


# Step 4.5 Check whether the sum of crop share is 100% (optional)
# ================================================================================
# *********************************************************************************
import os
import re
import numpy as np
import rasterio

def sum_rasters_for_year(folder_path, year):
    pattern = re.compile(rf"crop_share_{year}_layer_(\d+)\.tif$")
    sum_array = None
    profile = None
    first = True
    tif_files = [
        f for f in os.listdir(folder_path)
        if pattern.match(f)
    ]
    selected_files = []
    for f in tif_files:
        layer_num = int(pattern.match(f).group(1))
        if 1 <= layer_num <= 28:
            selected_files.append(f)
    if not selected_files:
        print(f"jump no crop_share_{year}_layer_1~28.tif : {folder_path}")
        return None, None
    for filename in sorted(selected_files):
        filepath = os.path.join(folder_path, filename)
        with rasterio.open(filepath) as src:
            data = src.read(1)
            if first:
                sum_array = np.zeros_like(data, dtype=np.float64)
                profile = src.profile
                first = False
            if src.nodata is not None:
                mask = data != src.nodata
                sum_array[mask] += data[mask]
            else:
                sum_array += data
    profile.update(dtype=rasterio.float64)
    return sum_array, profile


def batch_process_crop_share_sum(parent_folder, output_folder, years):
    os.makedirs(output_folder, exist_ok=True)
    for year in years:
        folder_path = os.path.join(parent_folder, str(year))
        if os.path.isdir(folder_path):
            print(f"processing: {year}")
            sum_array, profile = sum_rasters_for_year(folder_path, year)
            if sum_array is not None:
                output_filename = f"crop_share_{year}_sum.tif"
                output_path = os.path.join(output_folder, output_filename)
                with rasterio.open(output_path, 'w', **profile) as dst:
                    dst.write(sum_array, 1)
                print(f"save to {output_path}")
            else:
                print(f"{year} no tiff data, jump")
        else:
            print(f"no folder {folder_path}, jump")


parent_path = r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_04\Crop_share"  # 替换为实际路径
output_path = r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_04\Crop_share\check_sum"       # 用于保存sum结果的目录
batch_process_crop_share_sum(parent_path, output_path, years=range(2010, 2021))



# *********************************************************************************


