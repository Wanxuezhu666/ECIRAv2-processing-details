
import rasterio
import numpy as np
import glob
import os


# Step 7.1 Calculate initial total AAI, Which could be larger than 100
#================================================================================

os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_07") 

def sum_total_AAI(input_folder, output_file):
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
    #sum_array[sum_array > max_value] = max_value
    profile.update(dtype=rasterio.float32, count=1)
    with rasterio.open(output_file, 'w', **profile) as dst:
        dst.write(sum_array, 1)
    print(f"Summed GeoTIFF saved as: {output_file}")

# Calculate initial total irrigated area, which could be > 100
for i in range(11):
    year = 2010 + i
    input_folder = f'Crop-specific_AAI/{year}'
    output_file = f'Total_AAI/Total_IR_A_no_revise_{year}.tif'
    sum_total_AAI(input_folder, output_file)



# 7.2 Constrain total AAI <= 100 ha per 1km grid
#================================================================================

os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_07") 

def total_AAI_max100(input_folder, output_folder, target_max=100):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.tif', '.tiff')):
            input_path = os.path.join(input_folder, filename)
            output_filename = filename.replace('no_revise_', '')
            output_path = os.path.join(output_folder, output_filename)
            with rasterio.open(input_path) as src:
                data = src.read(1)
                profile = src.profile
            data_clipped = np.minimum(data, target_max).astype(profile['dtype'])
            with rasterio.open(output_path, 'w', **profile) as dst:
                dst.write(data_clipped, 1)

total_AAI_max100('Total_AAI', 'Total_AAI_max100', target_max=100)


# 7.3 Calculate Total AAI loss after constraining within 100 ha (optional)
#================================================================================

os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_07") 

def total_AAI_lose(folder1, folder2, out_folder, start_year=2010, end_year=2020):
    os.makedirs(out_folder, exist_ok=True)
    for year in range(start_year, end_year + 1):
        file1 = os.path.join(folder1, f"Total_IR_A_no_revise_{year}.tif")
        file2 = os.path.join(folder2, f"Total_IR_A_{year}.tif")
        out_file = os.path.join(out_folder, f"Total_IR_A_lose_{year}.tif")
        with rasterio.open(file1) as src1, rasterio.open(file2) as src2:
            data1 = src1.read(1).astype(float)
            data2 = src2.read(1).astype(float)
            diff = data1 - data2
            profile = src1.profile
            profile.update(dtype='float32')
            with rasterio.open(out_file, 'w', **profile) as dst:
                dst.write(diff.astype('float32'), 1)
        print(f"Saved difference for year {year}: {out_file}")


total_AAI_lose("Total_AAI", "Total_AAI_max100", "Total_AAI_lose")


# 7.4 Calculate calibration value to constrain Total AAI <= 100
#================================================================================

os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_07") 

def divide_geotiff(A_path, B_path, out_path, out_nodata=None):
    with rasterio.open(A_path) as srcA, rasterio.open(B_path) as srcB:
        A = srcA.read(1).astype(float)
        B = srcB.read(1).astype(float)
        nodata_A = srcA.nodata
        mask_A = (A == nodata_A) if nodata_A is not None else np.zeros_like(A, dtype=bool)
        C = np.full(A.shape, fill_value=np.nan, dtype=float)  # Initialize output array with NaNs
        valid_mask = ~mask_A  # Pixels valid for calculation
        zero_B_mask = (B == 0) & valid_mask
        C[zero_B_mask] = 1
        valid_div_mask = (B != 0) & valid_mask
        C[valid_div_mask] =  B[valid_div_mask]/A[valid_div_mask]
        if out_nodata is None:
            out_nodata = nodata_A if nodata_A is not None else -9999
        C[np.isnan(C)] = out_nodata
        profile = srcA.profile
        profile.update(
            dtype=rasterio.float32,
            nodata=out_nodata
        )
        with rasterio.open(out_path, 'w', **profile) as dst:
            dst.write(C.astype(rasterio.float32), 1)


def calibration_crop_AAI(folder_A, folder_B, output_folder, start_year=2010, end_year=2020):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    for year in range(start_year, end_year + 1):
        file_A = os.path.join(folder_A, f"Total_IR_A_no_revise_{year}.tif")
        file_B = os.path.join(folder_B, f"Total_IR_A_{year}.tif")
        out_file = os.path.join(output_folder, f"Calibration_IR_A_{year}.tif")
        if os.path.exists(file_A) and os.path.exists(file_B):
            print(f"Processing year {year}...")
            divide_geotiff(file_A, file_B, out_file)
        else:
            print(f"Files for year {year} missing, skipped.")


calibration_crop_AAI('Total_AAI', 'Total_AAI_max100', 'Calibration', 2010, 2020)


# 7.5 Generate final crop-specific AAI
# Final crop AAI = initial crop AAI (in step 6.3) * calibration (in step 7.4)
#================================================================================

import os
import glob
import rasterio
import numpy as np

os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\Step_07") 

def multiply_geotiff(input_path1, input_path2, output_path):
    with rasterio.open(input_path1) as src1, rasterio.open(input_path2) as src2:
        data1 = src1.read(1)
        data2 = src2.read(1)
        result = data1 * data2
        nodata = src1.nodata
        if nodata is not None:
            result[(data1 == nodata) | (data2 == nodata)] = nodata
        result = np.round(result, 2) 
        profile = src1.profile
        profile.update(dtype=rasterio.float32, count=1, compress='lzw')
        with rasterio.open(output_path, 'w', **profile) as dst:
            dst.write(result.astype(rasterio.float32), 1)

def calculation_crop_AAI(start_year=2010, end_year=2020):
    for year in range(start_year, end_year + 1):
        input1_dir = f"Crop-specific_AAI/{year}"
        input2_path = f"Calibration/Calibration_IR_A_{year}.tif"
        output_dir = f"E:/01_Reseach_papers/R1_irrigation_grid_map/Depository/ECIRA_v2/Crop_IR/{year}"
        os.makedirs(output_dir, exist_ok=True)
        tifs = glob.glob(f"{input1_dir}/*.tif")
        for tif_path in tifs:
            tif_name = os.path.basename(tif_path).replace("no_revise_", "")
            output_path = f"{output_dir}/{tif_name}"
            multiply_geotiff(tif_path, input2_path, output_path)
        print (f"Finished {year}")


calculation_crop_AAI()

# Crop AAI range: 1-100

# check_double_folder(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\ECIRA_v2\Crop_IR")
# see Step 9


# 7.6 Calculate Total AAI
#================================================================================

os.chdir(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\ECIRA_v2") 

def calculate_total_AAI(input_folder, output_file, max_value = 100):
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
    sum_array[sum_array > max_value] = max_value
    profile.update(dtype=rasterio.float32, count=1, compress='lzw')
    with rasterio.open(output_file, 'w', **profile) as dst:
        dst.write(sum_array, 1)
    print(f"Summed GeoTIFF saved as: {output_file}")


# total irrigated area
for i in range(11):
    year = 2010 + i
    input_folder = f'Crop_IR/{year}'
    output_file = f'Total_IR/Total_IR_A_{year}.tif'
    calculate_total_AAI(input_folder, output_file)


# check_single_folder(r"E:\01_Reseach_papers\R1_irrigation_grid_map\Depository\ECIRA_v2\Total_IR", threshold=100)
# see Step 9
