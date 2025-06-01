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
  
_Input data source:_

## Step 1: Generating NUTS2-level annual total AAI for 2010-2020    
**Method:** Manual (see the manuscript)  

## Step 2: Generating NUTS2-level annual crop-specific AAI for 2010-2020   
**Method:** Manual (see the manuscript)  

## Step 3: Generating 1km gridded AEI in 2010   
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

## Step 4: Generating annual 1km gridded crop-specific share and growing area for 2010–2020
 - 4.1	Split the multi-layer raster data from DGPCM into individual single-layer rasters. Layer 0 is **UAA**, layers 1–28 are **expected crop growing share.**  
   (Done in Python: **_Step_4_Crop_share.py → Section 4.1_**).
   
 - 4.2	Revise UAA maximum (provided by the ‘weight’ column in DGPCM) as 100 hectares in each 1km pixel.
   Note this is not the final UAA, we will update the UAA further after calculating total irrigated area. **（Update compared to ECRIA version 1）**  
   The updated UAA = maximum (UAA here, total AAI)
   (Done in Python: **_Step_4_Crop_share.py → Section 4.2_**).
   
 - 4.3	Calculate UAA loss caused by revising the maximum UAA to 100 hectares  
   (optional, Done in Python: **_Step_4_Crop_share.py → Section 4.3_**).
   
 - 4.4  Note that we aggregated some crop types as follows,  
   (Done in Python: **_Step_4_Crop_share.py → Section 4.4_**)

| ID |     Eurostat 2010 category     | ECIRA | DGPCM|
| -- | ------------------------------ | ------|----- |
| 1  | Cereals excluding maize & rice |  CERE |  -   |
| 1.1| Soft wheat                     |  -    | SWHE |
| 1.2| Durum wheat                    |  -    | DWHE |
| 1.3| Barley                         |  -    | BARL |
| 1.4| Rye                            |  -    | RYEM |
| 1.5| Oats                           |  -    | OATS |
| 1.6| Other cereals                  |  -    | OCER |
| 2  | Maize (green and grain)        | LMAIZ | LMAIZ|
| 3  | Rice                           | PARI  | PARI |
| 4  | Pulses                         | PULS  | PULS |
| 5  | Potato                         | POTA  | POTA |
| 6  | Sugar beet                     | SUGB  | SUGB |
| 7  | Rape and turnip rape           | LRAPE | LRAPE|
| 8  | Sunflower                      | SUNF  | SUNF |
| 9  | Textile crops                  | TEXT  | TEXT |
| 10 | Fresh vegetable, melon, strawberry - open field | TOMA_OVEG | TOMA_OVEG |
| 11 | Temporary and permanent grass  | GRAS  | GRAS |
| 12 | Other crops on arable land     | OTHER |   -  |
| 13 | Fruit & berry planatations     | APPL_OFRU | APPL_OFRU|
| 14 | Citrus planatations            | CITR  | CITR |
| 15 | Olive planatations             | OLIVGR|OLIVGR|
| 16 | Vineyards                      | VINY  | VINY |

Note: OTHER = ROOF + SOYA + TOBA + OIND + FLOW + OFAR + NURS + OCRO in DGPCM

- 4.5 Check whether the sum of 16 crop shares is 100% (optional)
(Done in Python: **_Step_4_Crop_share.py → Section 4.5_**)

## Step 5: Generating crop-specific AEI for 2010–2020
- 5.1	At 1km gridded level, multiplying AEI generated in Step 03 and crop share in Step 4.4 to get crop-specific irrigation area for 16 crop types for year 2010-2020  
  **_Crop AEI = crop area * AEI/UAA = crop share * UAA * AEI/UAA = crop share * AEI_**   
  (Done in Python: **_Step_5_Crop_AEI.py → Section 5.1_**, ha * 1000,000).
  
- 5.2 Conducting Zonal statistics for crop-specific AEI (generated in Step 5.1) at the NUTS2 level.   
  (Done in Python: **_Step_5_Crop_AEI.py → Section 5.2_**).

## Step 6: Calibration crop-specific AEI
- 6.1	We calculated crop-specific, year-specific AAI calibration coefficients of each NUTS2 unit.  
  (Done in Python: **_Step_6_Calibration_crop_AEI.py → Section 6.1_**)  

- 6.2	Generating 1 km gridded AAI calibration coefficients  
  (Done in Python: **_Step_6_Calibration_crop_AEI.py → Section 6.2_**)
We matched the above NUTS2 level coefficients (generated in step 6.1) with THE 1 km grid (each grid contains NUTS2 code), to generate grid-level AAI calibration coefficients.

**How to generate crop grids with NUTS2 ID?**    
Done in Python: _01_Get_NUTS_ID_for_grid.py_

- 6.3	Generating 1 km gridded crop-specific, year-specific AAI  
  (Done in Python: **_Step_6_Calibration_crop_AEI.py → Section 6.3_**)
Multiplying AAI calibration coefficients (generated in step 6.2) with crop-AEI (generated in step 5.2).

## Step 7: Constrain total AAI <= 100 ha per 1km grid (Update compared to ECRIA version 1)  
- 7.1 Calculate initial total AAI (= sum of crop-specific AAI generated in step 6.3), which could be larger than 100.   
  (Done in Python: **_Step_7_Constrain_AAI_max_100.py → Section 7.1_**)
  
- 7.2 Constrain the total AAI <= 100 ha for each 1km grid  
  (Done in Python: **_Step_7_Constrain_AAI_max_100.py → Section 7.2_**)
  
- 7.3 Calculate Total AAI loss after constraining within 100 ha (optional)
  (Done in Python: **_Step_7_Constrain_AAI_max_100.py → Section 7.3_**)
  
- 7.4 Calculate calibration value to constrain Total AAI <= 100
  AAI_calibration_100 = 100 / sum of crop-specific AAI (generated in step 6.3)
  (Done in Python: **_Step_7_Constrain_AAI_max_100.py → Section 7.4_**)
  
- 7.5 Generate final crop-specific AAI
  **_Final crop AAI = initial crop AAI (in step 6.3) * AAI_calibration_100 (in step 7.4)_**
  (Done in Python: **_Step_7_Constrain_AAI_max_100.py → Section 7.5_**)
  
- 7.6 Update the total AAI
  (Done in Python: **_Step_7_Constrain_AAI_max_100.py → Section 7.6_**)

## Step 8: Generate new UAA, crop growing and rainfed area (Update compared to ECRIA version 1)
- 8.1 Generate new UAA = maximum (old UAA from DGPCM 'weight' in step 4.1, total AAI in step 7.6)   
  (Done in Python: **_Step_8_Crop_growing_area.py → Section 8.1_**)
  
- 8.2 Update crop growing area = UAA (step 8.1) * crop share (step 4.4)   
  Note, this is not the final crop growing area!!! The final one is in step 8.5.   
  (Done in Python: **_Step_8_Crop_growing_area.py → Section 8.2_**)
  
- 8.3 Calculate crop-specific rainfed area   
  Crop rainfed area = crop growing area (step 8.2) - crop irrigated area (step 7.5)   
  If the crop rainfed area is negative, revised as 0.   
  (Done in Python: **_Step_8_Crop_growing_area.py → Section 8.3_**)
  
- 8.4 Calculate the total rainfed area = sum of crop-specific rainfed area   
  (Done in Python: **_Step_8_Crop_growing_area.py → Section 8.4_**)
  
- 8.5 Update the crop growing area    
  Crop growing area = crop irrigated area (step 7.5) + crop rainfed area (step 8.3)   
  This is the final crop growing area!!!   
  (Done in Python: **_Step_8_Crop_growing_area.py → Section 8.5_**) 

## Step 9: Quick check data
   Check whether the pixel values exceed 100.
   (Done in Python: **_Step_9_Check_data.py_**) 







