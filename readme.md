# Pakistan Tehsil Hazard Risk Preprocessing

This project prepares tehsil-level hazard risk data for a GIS dashboard. The preprocessing notebook combines rainfall, temperature, earthquake, and boundary data into clean CSV outputs plus a map-ready GeoJSON file.

## What The Pipeline Does

The notebook [`preprocessing.ipynb`](preprocessing.ipynb) performs these steps:

1. Loads raw NASA POWER-style rainfall and temperature CSV files.
2. Standardizes column names and creates daily dates from `YEAR` and `DOY`.
3. Merges rainfall and temperature by latitude, longitude, and date.
4. Summarizes annual weather values for each grid point.
5. Spatially joins weather grid points to Pakistan tehsil polygons.
6. Spatially joins earthquake events to tehsil polygons.
7. Creates rule-based flood, heatwave, earthquake, and overall risk scores.
8. Exports dashboard-ready CSV and GeoJSON files.

## Folder Structure

```text
GIS DASHBOARD/
|-- preprocessing.ipynb
|-- README.md
|-- Data/
    |-- Raw Weather/
    |   |-- *rainfall*.csv
    |   |-- *temperature*.csv
    |   |-- earthquake.csv
    |   |-- pakistan_tehsils.json
    |-- Processed/
        |-- weather_combined.csv
        |-- weather_annual_grid_summary.csv
        |-- weather_tehsil_summary.csv
        |-- earthquake_tehsil_summary.csv
        |-- final_tehsil_summary.csv
        |-- final_tehsil_risk_dataset.csv
        |-- final_tehsil_risk_map.geojson
```

## Setup

Create and activate a Python environment, then install the required packages:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install pandas geopandas folium jupyter
```

If `geopandas` installation fails on Windows, install it with Conda instead:

```powershell
conda install -c conda-forge geopandas folium jupyter
```

## How To Run

Start Jupyter from the project root:

```powershell
jupyter notebook
```

Open [`preprocessing.ipynb`](preprocessing.ipynb), then run all cells from top to bottom.

The notebook uses relative paths, so it expects the current working directory to be the project folder containing `Data/`.

## Input Files

| File | Purpose |
| --- | --- |
| `Data/Raw Weather/*rainfall*.csv` | Daily rainfall grid data |
| `Data/Raw Weather/*temperature*.csv` | Daily temperature grid data |
| `Data/Raw Weather/earthquake.csv` | Earthquake event data with latitude, longitude, depth, and magnitude |
| `Data/Raw Weather/pakistan_tehsils.json` | Pakistan tehsil boundary polygons |

## Main Outputs

| Output | Description |
| --- | --- |
| `weather_combined.csv` | Daily merged rainfall and temperature records |
| `weather_annual_grid_summary.csv` | Annual weather statistics by grid point |
| `weather_tehsil_summary.csv` | Weather statistics aggregated by tehsil |
| `earthquake_tehsil_summary.csv` | Earthquake statistics aggregated by tehsil |
| `final_tehsil_summary.csv` | Combined weather and earthquake summary |
| `final_tehsil_risk_dataset.csv` | Final tehsil risk scores and recommendations |
| `final_tehsil_risk_map.geojson` | Map-ready tehsil polygons with risk attributes |

## Risk Scoring Rules

The current scoring is rule-based and easy to adjust in the helper functions inside the notebook.

| Hazard | Input Column | Rule |
| --- | --- | --- |
| Flood | `max_rainfall` | `>= 80` -> 90, `>= 50` -> 70, `>= 20` -> 40, otherwise 10 |
| Heatwave | `max_temperature` | `>= 45` -> 90, `>= 40` -> 75, `>= 35` -> 50, otherwise 20 |
| Earthquake | `max_magnitude` | `>= 6` -> 90, `>= 5` -> 75, `>= 4` -> 50, otherwise 20 |

The final `overall_risk_score` is the average of the flood, heatwave, and earthquake scores.

| Overall Score | Risk Level |
| --- | --- |
| `>= 75` | Critical |
| `>= 60` | High |
| `>= 40` | Medium |
| `< 40` | Low |

## Notes

- Keep the raw file names descriptive. The notebook detects weather inputs using `*rainfall*.csv` and `*temperature*.csv`.
- The final GeoJSON keeps tehsils with no weather coverage and labels them as `No Data`.
- The optional Folium map at the end of the notebook is only for quick inspection. The dashboard should use `Data/Processed/final_tehsil_risk_map.geojson`.