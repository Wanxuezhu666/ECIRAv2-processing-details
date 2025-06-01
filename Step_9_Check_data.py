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


