# datainterface
Industrial Energy Data Exploration Interface

📊 Integrated Dataset

To generate the integrated dataset, execute the notebooks in the following order:

1️⃣ Data Cleaning (src/notebooks/data_cleaning):
* Processes raw data and outputs datasets in a tidy format.

2️⃣ Adjusted Implementation Cost Calculation (src/notebooks/arc_ppi):
* Computes adjusted implementation costs.
* Integrates the calculated values into the recc table.

3️⃣ Emissions Integration & Finalization (src/notebooks/emissions):
* Merges the assess table into the recc table.
* Calculates emissions data.
* Integrates emissions into the final Integrated IAC Dataset.

```
Repository File Structure

├── README.md
├── assets
│   ├── emissions_avoided_boxplot.png
│   ├── emissions_avoided_facetgrid.png
│   ├── impcost_boxplot_aggregate.png
│   ├── impcost_boxplot_by_year.png
│   ├── isalab-logo.svg
│   └── payback_boxplot_aggregate.png
├── data
│   ├── intermediate_data
│   │   ├── ARC_PPI_Draft.xlsx
│   │   ├── emission_factors_tidy.xlsx
│   │   ├── emissions_tidy.csv
│   │   ├── generation.csv
│   │   ├── iac_assess_tidy.csv
│   │   ├── iac_integrated.csv
│   │   ├── iac_recc_tidy.csv
│   │   ├── null_naics.csv
│   │   ├── ppi_tidy.csv
│   │   └── recc_integrated_ppi.csv
│   ├── processed_data
│   └── raw_data
│       ├── ARC.xlsx
│       ├── ARC_PPI.xlsx
│       ├── ARC_PPI_Draft.xlsx
│       ├── ARC_PPI_Mapping.xlsx
│       ├── Fuel_Emission_Factors.xlsx
│       ├── IAC_Database_20250208.xls
│       ├── annual_generation_state.xls
│       └── emission_annual.xlsx
├── environment.yml
├── output.png
└── src
    ├── notebooks
    │   ├── adj_impcost_boxplot.ipynb
    │   ├── arc_ppi.ipynb
    │   ├── data_cleaning.ipynb
    │   ├── emissions.ipynb
    │   ├── emissions_boxplot.ipynb
    │   ├── energy_savings_boxplot.ipynb
    │   └── fuel_emissions_factors.ipynb
    └── scripts
        ├── data_cleaning.py
        └── null_naics_check.py
```