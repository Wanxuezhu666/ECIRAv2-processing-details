"""
Updated: Wanxue Zhu (wanxue.zhu@agr.uni-goettingen.de)
Date: 2025-June-01
"""

import rasterio
import numpy as np
import glob
import os

os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository") 

# Step 8.1 Generate new UAA = maximum (old UAA, total AAI)
#================================================================================

def max_geotiff(tif1_path, tif2_path, out_path):
    with rasterio.open(tif1_path) as src1, rasterio.open(tif2_path) as src2:
        data1 = src1.read(1)
        data2 = src2.read(1)/10
        result = np.maximum(data1, data2)
        profile = src1.profile
        with rasterio.open(out_path, 'w', **profile) as dst:
            dst.write(result, 1)


for year in range(2010, 2021):
    tif1 = f"ECIRA_v2/Total_IR/Total_IR_A_{year}.tif"
    tif2 = f"Step_04/UAA_2010_2020_revised_100/UAA_{year}.tif"
    out = f"ECIRA_v2/UAA/UAA_{year}.tif"
    max_geotiff(tif1, tif2, out)

# check_single_folder(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\ECIRA_v2\UAA")
# See step 9

# Step 8.2 Update crop growing area = UAA (step 8.1) * crop share (step 4.4)
#================================================================================

from osgeo import gdal
import os

os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository") 

def crop_area_calculation(input_path_1, input_path_2, output_path):
    # Open the input datasets
    dataset_a = gdal.Open(input_path_1)
    band1_a = dataset_a.GetRasterBand(1)
    array_a = band1_a.ReadAsArray()
    dataset_b = gdal.Open(input_path_2)
    band1_b = dataset_b.GetRasterBand(1)
    array_b = band1_b.ReadAsArray()
    result_array = array_a*array_b/1000 #（现在是1000 * 100 ha）
    geotransform = dataset_a.GetGeoTransform()
    projection = dataset_a.GetProjection()
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    driver = gdal.GetDriverByName('GTiff')
    options = ['COMPRESS=LZW', 'TILED=YES'] 
    out_dataset = driver.Create(output_path, dataset_a.RasterXSize, dataset_a.RasterYSize, 1, gdal.GDT_Float32, options)
    out_dataset.SetGeoTransform(geotransform)
    out_dataset.SetProjection(projection)
    out_band1 = out_dataset.GetRasterBand(1)
    out_band1.WriteArray(result_array)
    out_band1.FlushCache()
    out_dataset = None
    dataset_a = None
    dataset_b = None

for num in range(11):
    year = num+2010
    print(f"start year {year}")
    for crop_id in range(30):
        crop_area_calculation(f'Step_04/Crop_share/{year}/crop_share_{year}_layer_{crop_id+1}.tif',
                              f'ECIRA_v2/UAA/UAA_{year}.tif',
                              f'Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_{crop_id+1}.tif')



check_double_folder(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_08\Crop_growing_area", 100)


# Step 8.3 Calculate crop-specific rainfed area
#================================================================================
from osgeo import gdal, gdalconst

os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository") 

def Difference_two_images(input_path1, input_path2, output_path):
    input_dataset1 = gdal.Open(input_path1, gdalconst.GA_ReadOnly)
    input_dataset2 = gdal.Open(input_path2, gdalconst.GA_ReadOnly)
    num_cols = input_dataset1.RasterXSize
    num_rows = input_dataset1.RasterYSize
    data_type = gdal.GDT_Float32
    output_dir = os.path.dirname(output_path)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    driver = gdal.GetDriverByName("GTiff")
    options = ['COMPRESS=LZW']
    output_dataset = driver.Create(output_path, num_cols, num_rows, 1, data_type, options)
    output_dataset.SetGeoTransform(input_dataset1.GetGeoTransform())
    output_dataset.SetProjection(input_dataset1.GetProjection())
    data1 = input_dataset1.GetRasterBand(1).ReadAsArray().astype(np.float32)
    data2 = input_dataset2.ReadAsArray().astype(np.float32)
    result_data = data1 - data2
    result_data[result_data < 0] = 0 # negative values set 0
    output_band = output_dataset.GetRasterBand(1)
    output_band.WriteArray(result_data)
    input_dataset1 = None
    input_dataset2 = None
    output_dataset = None


for num in range(11):
    year = num + 2010
    print(year)
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_29.tif", f"ECIRA_v2/Crop_IR/{year}/CERE_IR_A_{year}.tif",  f"ECIRA_v2/Crop_RF/{year}/CERE_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_7.tif",  f"ECIRA_v2/Crop_IR/{year}/LMAIZ_IR_A_{year}.tif", f"ECIRA_v2/Crop_RF/{year}/LMAIZ_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_16.tif", f"ECIRA_v2/Crop_IR/{year}/PARI_IR_A_{year}.tif",  f"ECIRA_v2/Crop_RF/{year}/PARI_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_18.tif", f"ECIRA_v2/Crop_IR/{year}/PULS_IR_A_{year}.tif",  f"ECIRA_v2/Crop_RF/{year}/PULS_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_17.tif", f"ECIRA_v2/Crop_IR/{year}/POTA_IR_A_{year}.tif",  f"ECIRA_v2/Crop_RF/{year}/POTA_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_22.tif", f"ECIRA_v2/Crop_IR/{year}/SUGB_IR_A_{year}.tif",  f"ECIRA_v2/Crop_RF/{year}/SUGB_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_8.tif",  f"ECIRA_v2/Crop_IR/{year}/LRAPE_IR_A_{year}.tif", f"ECIRA_v2/Crop_RF/{year}/LRAPE_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_23.tif", f"ECIRA_v2/Crop_IR/{year}/SUNF_IR_A_{year}.tif",  f"ECIRA_v2/Crop_RF/{year}/SUNF_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_25.tif", f"ECIRA_v2/Crop_IR/{year}/TEXT_IR_A_{year}.tif",  f"ECIRA_v2/Crop_RF/{year}/TEXT_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_27.tif", f"ECIRA_v2/Crop_IR/{year}/TOMA_OVEG_IR_A_{year}.tif", f"ECIRA_v2/Crop_RF/{year}/TOMA_OVEG_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_6.tif",  f"ECIRA_v2/Crop_IR/{year}/GRAS_IR_A_{year}.tif",  f"ECIRA_v2/Crop_RF/{year}/GRAS_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_30.tif", f"ECIRA_v2/Crop_IR/{year}/OTHER_IR_A_{year}.tif", f"ECIRA_v2/Crop_RF/{year}/OTHER_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_1.tif",  f"ECIRA_v2/Crop_IR/{year}/APPL_OFRU_IR_A_{year}.tif", f"ECIRA_v2/Crop_RF/{year}/APPL_OFRU_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_3.tif",  f"ECIRA_v2/Crop_IR/{year}/CITR_IR_A_{year}.tif",  f"ECIRA_v2/Crop_RF/{year}/CITR_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_15.tif", f"ECIRA_v2/Crop_IR/{year}/OLIVGR_IR_A_{year}.tif",f"ECIRA_v2/Crop_RF/{year}/OLIVGR_RF_A_{year}.tif")
    Difference_two_images(f"Step_08/Crop_growing_area/{year}/crop_area_{year}_layer_28.tif", f"ECIRA_v2/Crop_IR/{year}/VINY_IR_A_{year}.tif",  f"ECIRA_v2/Crop_RF/{year}/VINY_RF_A_{year}.tif")


check_double_folder(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\ECIRA_v2\Crop_RF",100)




# Step 8.4 Calculate the total rainfed area
#================================================================================


os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\ECIRA_v2") 

def sum_geotiffs(input_folder, output_file):
    geotiff_files = glob.glob(os.path.join(input_folder, '*.tif'))
    if not geotiff_files:
        raise ValueError("No GeoTIFF files found in the specified directory.")
    with rasterio.open(geotiff_files[0]) as src:
        profile = src.profile
        sum_array = np.zeros((src.height, src.width), dtype=np.float32)
    for file in geotiff_files:
        with rasterio.open(file) as src:
            data = src.read(1)  
            sum_array += data
    sum_array[sum_array > 100] = 100
    profile.update(dtype=rasterio.float32, count=1)
    with rasterio.open(output_file, 'w', **profile) as dst:
        dst.write(sum_array, 1)
    print(f"Summed GeoTIFF saved as: {output_file}")


# total rainfed area
for i in range(11):
    year = 2010 + i
    input_folder = f'Crop_RF/{year}'
    output_file = f'Total_RF/Total_RF_A_{year}.tif'
    sum_geotiffs(input_folder, output_file)

check_single_folder(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\ECIRA_v2\Total_RF",threshold = 100)

#----------Step 8.5 Generate new crop growing area----------------
#================================================================================

import os
import rasterio
import numpy as np

os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\ECIRA_v2") 

def add_geotiff(tif1_path, tif2_path, out_path):
    with rasterio.open(tif1_path) as src1, rasterio.open(tif2_path) as src2:
        data1 = src1.read(1).astype(np.float32)
        data2 = src2.read(1).astype(np.float32)
        result = data1 + data2
        profile = src1.profile
        profile.update(dtype=rasterio.float32,compress='lzw', tiled=True)
        with rasterio.open(out_path, 'w', **profile) as dst:
            dst.write(result, 1)

def batch_add(ir_root, rf_root, out_root):
    for year in range(2010, 2021):
        ir_folder = os.path.join(ir_root, str(year))
        rf_folder = os.path.join(rf_root, str(year))
        out_folder = os.path.join(out_root, str(year))
        os.makedirs(out_folder, exist_ok=True)
        for fname in os.listdir(ir_folder):
            if fname.endswith(".tif") and "_IR_" in fname:
                rf_name = fname.replace("_IR_", "_RF_")
                out_name = fname.replace("_IR_", "_")
                ir_path = os.path.join(ir_folder, fname)
                rf_path = os.path.join(rf_folder, rf_name)
                out_path = os.path.join(out_folder, out_name)
                add_geotiff(ir_path, rf_path, out_path)
        print(f"Processing year {year}")

# 示例调用
batch_add(
    ir_root=r"Crop_IR",
    rf_root=r"Crop_RF",
    out_root=r"Crop_A"
)

check_double_folder(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\ECIRA_v2\Crop_A",100)



