"""
Updated: Wanxue Zhu (wanxue.zhu@agr.uni-goettingen.de)
Date: 2025-June-01
"""

import rasterio
import numpy as np
import glob
import os

### Step 09: Quick check data

# This fold contains subfolders - years

def check_double_folder(base_folder, threshold):
    for year in range(2010, 2021):
        folder = os.path.join(base_folder, str(year))
        print(f"Folder: {year}")
        tifs = glob.glob(os.path.join(folder, "*.tif"))
        for tif_path in tifs:
            with rasterio.open(tif_path) as src:
                data = src.read(1).astype(np.float32)
                max_val = np.nanmax(data)
                count_over_100 = np.sum(data > threshold)
                tif_name = os.path.basename(tif_path)
                print(f"  {tif_name}: max = {max_val}, >{threshold} pixels = {count_over_100}")

# No subfolder
def check_single_folder(folder, threshold):
    tifs = glob.glob(os.path.join(folder, "*.tif"))
    for tif_path in tifs:
        with rasterio.open(tif_path) as src:
            data = src.read(1).astype(np.float32)
            max_val = np.nanmax(data)
            count = np.sum(data > threshold)
            fname = os.path.basename(tif_path)
            print(f"{fname} | max: {max_val} | count > {threshold}: {count}")



check_single_folder(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\ECIRA_v2\UAA", threshold=100)
check_single_folder(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\ECIRA_v2\Total_IR", threshold=100)
check_single_folder(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\ECIRA_v2\Total_RF", threshold=100)

check_max_over_100(r"E:\your_folder_path")

check_max_values(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\ECIRA_RF_v2")




check_max_and_count(r"ECIRA_total_v2")



# 计算 ECIRA total AAI at NUTS0 level

os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository") 

def add_field_shapfile(shapefile_path,tif_path,field_name):
    gdf = gpd.read_file(shapefile_path)
    with rasterio.open(tif_path) as src:
        affine = src.transform
        array = src.read(1)  # 读取第一个波段的数据
    stats = zonal_stats(gdf.geometry, array, affine=affine, stats='sum', nodata=-9999)
    gdf[field_name] = [int(stat['sum'] ) if stat['sum'] is not None else 0 for stat in stats]
    return(gdf)


def add_field_shapfile_more(gdf,tif_path,field_name):
    with rasterio.open(tif_path) as src:
        affine = src.transform
        array = src.read(1)  # 读取第一个波段的数据
    stats = zonal_stats(gdf.geometry, array, affine=affine, stats='sum', nodata=-9999)
    gdf[field_name] = [int(stat['sum'] ) if stat['sum'] is not None else 0 for stat in stats]
    return(gdf)



Crop = add_field_shapfile('E:/01_Reseach_papers/R1_irrigation_grid_map/Data/NUTS_shapefile/NUTS_RG_01M_2010_3035_NUTS0.shp',
                         f'ECIRA_v2/Total_IR/Total_IR_A_2010.tif',
                          'Year2010')
for i in range(10):
    Crop = add_field_shapfile_more(Crop,f'ECIRA_v2/Total_IR/Total_IR_A_{2011+i}.tif',f'Year{i+2011}')
    print(i+2011)
    i += 1


Crop.to_file(f'Step_08/Final_AAI_loss/Total_AAI_NUTS0.shp')
Crop.to_excel('Step_08/Final_AAI_loss/Total_AAI_NUTS0.xlsx', index=False)


# ------------计算NUTS2尺度得AAI loss-----------------


Crop = add_field_shapfile(r'E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_05\NUS2010_NUTS2_01m_3035.shp',
                         f'ECIRA_v2/Total_IR/Total_IR_A_2010.tif',
                          'Year2010')
for i in range(10):
    Crop = add_field_shapfile_more(Crop,f'ECIRA_v2/Total_IR/Total_IR_A_{2011+i}.tif',f'Year{i+2011}')
    print(i+2011)
    i += 1


Crop.to_file(f'Step_08/Final_AAI_loss/Total_AAI_NUTS2.shp')
Crop.to_excel('Step_08/Final_AAI_loss/Total_AAI_NUTS2.xlsx', index=False)








