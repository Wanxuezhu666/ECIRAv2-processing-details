# Processing details of the Euprean Crop-specific Irrigation Area Dataset Version 2 (ECIRAv2)

**Contact:** Wanxue Zhu (wanxue.zhu@agr.uni-goettingen.de)  
*Department of Crop Sciences, University of Göttingen, Von-Siebold-Str. 8, 37075 Göttingen, Germany*  
**Updated:** 01 June 2025

The European Crop-specific IRrigated Area Dataset (ECIRA) provides data on the actual irrigated and rainfed area for specific crops across 28 European countries from 2010 to 2020, with a spatial resolution of 1 km and using the EPSG: 3035 projection.

16 crop types are included: cereals (excluding maize and rice), maize, rice, pulses, potatoes, sugar beets, rapeseed and turnip rapeseed, sunflower, textile crops, open-field vegetables, melons, strawberries, grasslands, fruits and berries, citrus, olives, vineyards, and other crops.

28 European countries are included: Austria, Belgium, Bulgaria, Cyprus, the Czech Republic, Germany, Denmark, Estonia, Greece, Spain, Finland, France, Croatia, Hungary, Ireland, Italy, Lithuania, Luxembourg, Latvia, Malta, Netherlands, Poland, Portugal, Romania, Sweden, Slovenia, Slovakia, and the United Kingdom.

This document outlines the detailed methodology used to generate the ECIRA dataset version 2, which is organized into distinct processing steps.  
**Compared to version 1, the main improvement is the addition of a calibration step to ensure that the total AAI does not exceed 100 hectares per 1-km grid.**

Abbreviations:

- **AAI** (in hectares): Irrigated area, namely area actually received irrigation.
- **AEI** (in hectares): Irrigable area, namely area equipped with irrigation infrastructure without considering the actual irrigation is applied or not.
- **UAA** (in hectares): Utilized agricultural land.
Input data source:
