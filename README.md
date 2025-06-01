# Processing details of the European Crop-specific Irrigation Area Dataset Version 2 (ECIRAv2)

**Contact:** Wanxue Zhu (wanxue.zhu@agr.uni-goettingen.de)  
*Department of Crop Sciences, University of Göttingen, Von-Siebold-Str. 8, 37075 Göttingen, Germany*  
**Updated:** 01 June 2025

The European Crop-specific IRrigated Area Dataset (ECIRA) provides data on the actual irrigated and rainfed area for specific crops across 28 European countries from 2010 to 2020, with a spatial resolution of 1 km and using the EPSG: 3035 projection.

16 crop types are included: cereals (excluding maize and rice), maize, rice, pulses, potatoes, sugar beets, rapeseed and turnip rapeseed, sunflower, textile crops, open-field vegetables, melons, strawberries, grasslands, fruits and berries, citrus, olives, vineyards, and other crops.

28 European countries are included: Austria, Belgium, Bulgaria, Cyprus, the Czech Republic, Germany, Denmark, Estonia, Greece, Spain, Finland, France, Croatia, Hungary, Ireland, Italy, Lithuania, Luxembourg, Latvia, Malta, Netherlands, Poland, Portugal, Romania, Sweden, Slovenia, Slovakia, and the United Kingdom.

This document outlines the detailed methodology used to generate the ECIRA dataset version 2, which is organized into distinct processing steps.  
**Compared to version 1, the main improvement is adding a calibration step to ensure that the sum of 16 crop-specific irrigated (rainfed, total) areas does not exceed 100 hectares per 1-km grid.**

Abbreviations:

- **AAI** (in hectares): Irrigated area, namely the area actually receiving irrigation.
- **AEI** (in hectares): Irrigable area, namely the area equipped with irrigation infrastructure, without considering whether  the actual irrigation is applied or not. (AEI >= AAI)
- **UAA** (in hectares): Utilized agricultural land.
Input data source:

## 1. Generating NUTS2-level annual total AAI for 2010-2020    
**Method:** Manual (see the manuscript)  

## 2. Generating NUTS2-level annual crop-specific AAI for 2010-2020   
**Method:** Manual (see the manuscript)  

## 3. Generating 1km gridded AEI in 2010   
**Method:** QGIS + Python (Step_03_AEI_1km.py)
- 3.1 Transfer GMIA 0.01 arc degree raster data for Europe (*i.e., AEI 2005 at 0.01 arc degree, corresponding to 1.11 km at the equator*) into a points shapefile. 
(Done in QGIS)   
- 3.2 Transfer HID 5 arc min raster data for Europe (*i.e., AEI 2010 at 5 arc min, corresponding to approximately 9.3 km at the equator*) into a grid vector shapefile.
(Done in QGIS)   
- 3.3 Perform Zonal Statistical calculations to compute the mean of all points within the 5 arc minute grids generated in step 2, and create a new grid shapefile.
(Done in QGIS)
- 3.4 Resample GMIA (AEI 2005) from 0.01 arc degree to 1 km grid.
(Done in Python: Step_3_AEI_1km.py → Section 3.4).
- 3.5 Convert the shapefile generated in step 3.3 into a TIFF file. This will create the GMIA AEI 2005 5 arc min TIFF file.  
(Done in Python: Step_3_AEI_1km.py → Section 3.5).
- 3.6 At the 5-arc-minute grid, calculate the correction coefficients between GMIA (AEI 2005) and HID (AEI 2010) to obtain the coefficients at 5 arc min, then resample them to 1km.
(Done in Python: Step_3_AEI_1km.py → Section 3.6).
- 3.7 At 1km grid level, multiply the GMIA obtained in step 3.4 by the coefficients obtained in step 3.6.  
(Done in Python: Step_3_AEI_1km.py → Section 3.7).
- 3.8 A revision was made to constrain the total AEI to a maximum of 100 hectares.  
(Done in Python: Step_3_AEI_1km.py → Section 3.8)
- 3.9 Add data for Cyprus using AEI 2010 1km from the resampling of 5 arc min.  
   **（Update compared to ECRIA version 1）**  
As the AEI 2005 dataset at 0.01 arc degree resolution does not include data for Cyprus, we used data for Cyprus from the AEI 2010 dataset at 5 arc minutes resolution. Specifically, we resampled the AEI 2010 data from 5 arc minutes to 1 km resolution and integrated the Cyprus data into the AEI 2010 dataset at 1 km produced in Step 3.8, thus generating the final AEI for 2010 at 1 km resolution.









