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

## Integrated Dataset
To generate an integrated dataset execute the notebooks in the following order:

(1) src/notebooks/data_cleaning: generates datasets in tidy format
(2) src/notebooks/arc_ppi: calculates adjusted implementation cost and integrates the values into the recc table
(3) src/notebooks/emissions: integrates assess table into the recc table; calculates emissions and integrates the values into the final integrated iac dataset
