# datainterface
Industrial Energy Data Exploration Interface

```
Repository File Structure

├── README.md
├── assets
├── data
│   ├── intermediate_data
│   ├── processed_data
│   └── raw_data
│       ├── ARC_PPI_Mapping.xlsx
│       ├── Fuel_Emission_Factors.xlsx
│       ├── IAC_Database_20250208.xls
│       └── annual_generation_state.xls
└── src
    ├── data_cleaning.ipynb
    ├── arc_ppi.ipynb
    └── eda.ipynb
```

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