# -------  IMPORT LIBRARIES ------- 

import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import janitor
from janitor import clean_names

# -------  IMPORT DATA ------- 

# ------- define paths -------
# define relative path
relative_path = Path('data/raw_data/') # run the script from the root folder <python src/scripts/data_cleaning.py>

# get absolute path
absolute_path = relative_path.resolve()
print(absolute_path)

# declare file names
filename_iac = "IAC_Database_20250208.xls"
filename_ppi = "ARC_PPI_Draft.xlsx"
filename_generation = "annual_generation_state.xls"
filename_emissions = "emission_annual.xlsx"

# ------- import data -------

# import IAC database
iac_df = pd.read_excel(absolute_path/filename_iac, sheet_name=None)
# import all RECC* sheets from the IAC database excel file  
all_sheets = pd.read_excel(absolute_path/filename_iac, sheet_name=None) 
# filter sheets that match the pattern
recc_sheets = {name: data for name, data in all_sheets.items() if name.startswith('RECC')}
# combine matching sheets into a single DataFrame
iac_recc_df = pd.concat(
    [sheet.assign(RECC=name) for name, sheet in recc_sheets.items()],
    ignore_index=True
)

# import ASSESS table
iac_assess_df = all_sheets['ASSESS']

# import PPI sheet
ppi_df = pd.read_excel(absolute_path/filename_ppi, sheet_name="PPI")

# import Electricity Generation table
generation_df = pd.read_excel(absolute_path/filename_generation, sheet_name="Net_Generation_1990-2023 Final", skiprows=1)

# import Electricity Emissions table
emissions_df = pd.read_excel(absolute_path/filename_emissions, sheet_name="State Emissions")

# -------  NORMALIZE DATA ------- 

# Transform the iac_recc table from wide to long format
# Requirements
# 1. Keep all common columns
# 2. Create four rows for each input row (one for each energy source usage ranking: Primary, Secondary, Tertiary, Quaternary)
# 3. Maintain the relationship between energy source codes and their associated values: SOURCCODE, CONSERVED, SOURCONSV, SAVED
# 4. Order the columns to maintain the original dataframe structure
# Create a function to trasnform the recc table from wide to long format
def transform_recc_data(df):
    """
    Transform wide format usage data to long format by unpivoting usage-related columns.
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame in wide format
    
    Returns:
    pandas.DataFrame: Transformed DataFrame in long format
    """
    
    # Common columns that will be repeated for each usage record
    common_cols = ['SUPERID', 'ID', 'AR_NUMBER', 'APPCODE', 'ARC2', 
                  'IMPSTATUS', 'IMPCOST', 'REBATE', 'INCREMNTAL', 
                  'FY', 'IC_CAPITAL', 'IC_OTHER', 'PAYBACK', 'BPTOOL']
    
    # Create list of usage types
    usage_types = ['P', 'S', 'T', 'Q']
    
    # Initialize list to store transformed data
    transformed_data = []
    
    # Iterate through each row in the original dataframe
    for _, row in df.iterrows():
        # For each usage type, create a new record
        for usage in usage_types:
            new_row = {col: row[col] for col in common_cols}
            
            # Add usage-specific columns
            sourccode_col = f'{usage}SOURCCODE'
            conserved_col = f'{usage}CONSERVED'
            sourconsv_col = f'{usage}SOURCONSV'
            saved_col = f'{usage}SAVED'
            
            new_row['SOURCE_RANK'] = f'{usage}SOURCCODE'
            new_row['SOURCCODE'] = row.get(sourccode_col, '')
            new_row['CONSERVED'] = row.get(conserved_col, '')
            new_row['SOURCONSV'] = row.get(sourconsv_col, '')
            new_row['SAVED'] = row.get(saved_col, '')
            
            transformed_data.append(new_row)
    
    # Create new dataframe from transformed data
    result_df = pd.DataFrame(transformed_data)
    
    # Ensure columns are in the desired order
    column_order = common_cols[:7] + ['SOURCE_RANK', 'SOURCCODE', 'CONSERVED', 
                                    'SOURCONSV', 'SAVED'] + common_cols[7:]
    
    return result_df[column_order]

# Transform recc dataset from wide to long
iac_recc_tidy_df = transform_recc_data(iac_recc_df)

# #### Transform the iac_assess table from wide to long format
# Requirements
# 1. Keep all common columns
# 2. Convert *_plant_usage and *_plant_cost columns into rows under the plant_usage and plant_cost columns, and add a separate column for the source code.
# 4. Order the columns to maintain the original dataframe structure

def transform_assess_data(df):
    """
    Transform wide format plant data to long format by converting *_plant_usage 
    and *_plant_cost columns into rows.
    
    Parameters:
    df (pandas.DataFrame): Input DataFrame in wide format
    
    Returns:
    pandas.DataFrame: Transformed DataFrame in long format
    """
    # Common columns that will be preserved
    id_vars = ['CENTER', 'FY', 'SIC', 'NAICS', 'STATE', 'SALES', 
               'EMPLOYEES', 'PLANT_AREA', 'PRODUCTS', 'PRODUNITS', 
               'PRODLEVEL', 'PRODHOURS', 'NUMARS']
    
    # Melt cost columns
    cost_df = pd.melt(
        df,
        id_vars=['ID'] + id_vars,
        value_vars=[col for col in df.columns if col.endswith('_plant_cost')],
        var_name='source_code',
        value_name='plant_cost'
    )
    # Clean up source_code by removing '_plant_cost'
    cost_df['source_code'] = cost_df['source_code'].str.replace('_plant_cost', '')
    
    # Melt usage columns
    usage_df = pd.melt(
        df,
        id_vars=['ID'] + id_vars,
        value_vars=[col for col in df.columns if col.endswith('_plant_usage')],
        var_name='source_code',
        value_name='plant_usage'
    )
    # Clean up source_code by removing '_plant_usage'
    usage_df['source_code'] = usage_df['source_code'].str.replace('_plant_usage', '')
    
    # Merge cost and usage dataframes
    result_df = cost_df.merge(
        usage_df,
        on=['ID'] + id_vars + ['source_code'],
        how='outer'
    )
    
    # Create ordered categorical for source_code
    source_order = ['EC', 'ED', 'EF'] + [f'E{i}' for i in range(2, 13)] + [f'W{i}' for i in range(7)]
    result_df['source_code'] = pd.Categorical(result_df.source_code, categories=source_order, ordered=True)
    
    # Remove rows where both plant_cost and plant_usage are NA
    result_df = result_df.dropna(subset=['plant_cost', 'plant_usage'], how='all')

    # Sort by ID and source_code and set ID as index
    # result_df = result_df.sort_values(by=['ID', 'source_code']).set_index('ID')
    result_df = result_df.sort_values(by=['ID', 'source_code'])
    
    return result_df

# Transform assess dataset from wide to long
iac_assess_tidy_df = transform_assess_data(iac_assess_df)

# #### Transform the ppi table from wide to long format
# Requirements
# 1. Keep all common columns
# 2. Convert year columns into rows under the year and ppi columns
# 4. Order the columns to maintain the original dataframe structure

#ppi_tidy_df = transform_ppi_data(ppi_df)
ppi_tidy_df = pd.melt(
    ppi_df,
    id_vars=['ARC', 'Description', 'Series ID', 'Industry', 'Product'],
    value_vars=[1987, 1988, 1989, 1990, 1991, 1992,
                   1993, 1994, 1995, 1996, 1997, 1998,
                   1999, 2000, 2001, 2002, 2003, 2004,
                   2005, 2006, 2007, 2008, 2009, 2010,
                   2011, 2012, 2013, 2014, 2015, 2016,
                   2017, 2018],
    var_name='year',
    value_name='ppi'
    )

ppi_tidy_df = ppi_tidy_df.sort_values(by=['year', 'ARC'])

# ### Transform the emissions table from wide to long format
# Requirements
# 1. Keep all common columns
# 2. Convert emission type columns into rows under the emission type columns and emissions columns
# 3. Add a column for units
# 4. Order the columns to maintain the original dataframe structure

emissions_df.columns = [col.replace('\n(Metric Tons)', '') 
                        for col in emissions_df.columns]
# Melt the dataframe
emissions_tidy_df = pd.melt(
    emissions_df,
    id_vars = ['State', 'Year', 'Producer Type', 'Energy Source'],
    value_vars = ['CO2', 'SO2', 'NOx'],
    var_name = 'emission_type',
    value_name = 'amount'
    )

# -------  CLEAN DATA ------- 

#------------------------ Clean data: ASSESS table ------------------------#

iac_assess_tidy_df = iac_assess_tidy_df.clean_names()
# strip whitespace from all string columns
for col in iac_assess_tidy_df.select_dtypes(include='object').columns:
    iac_assess_tidy_df[col] = iac_assess_tidy_df[col].str.strip()

#------------------------ Clean RECC table ------------------------#

# Replace old source coce for electricity values "E1" with "EC"
# Reason: E1 was replaced with EC, ED, and EF as of FY 95 (9/30/95)
# Reference: https://iac.university/technicalDocs/IAC_DatabaseManualv10.2.pdf
iac_recc_tidy_df.replace({'SOURCCODE':{'E1':'EC'}}, inplace=True)
iac_recc_tidy_df = iac_recc_tidy_df.clean_names()

#------------------------ Clean PPI table ------------------------#

ppi_tidy_df.rename(columns={'ARC': 'ARC2'}, inplace=True) # rename the column ARC to ARC2
ppi_tidy_df = ppi_tidy_df.clean_names()
# round ARC values to 4 decimal places
ppi_tidy_df['arc2'] = ppi_tidy_df['arc2'].round(4)
# replace "-" and "N/A" with 120 in the ppi column 
#--------- <TEMP until PPI values are collected> ----------#
ppi_tidy_df['ppi'] = ppi_tidy_df['ppi'].replace('-', 120)
ppi_tidy_df['ppi'].fillna(120, inplace=True)

#------------------------  Clean data: Electricity Generation table ------------------------#

generation_df = generation_df.rename(columns={'generation_megawatthours_': 'generation_megawatthours'})
generation_df['units'] = 'MWh' # add a column for units
generation_df = generation_df.clean_names()
# strip whitespace from all string columns
for col in generation_df.select_dtypes(include='object').columns:
    generation_df[col] = generation_df[col].str.strip()

#------------------------ Clean data: Electricity Emissions table ------------------------#

emissions_tidy_df = emissions_tidy_df.clean_names()
# strip whitespace from all string columns
for col in emissions_tidy_df.select_dtypes(include='object').columns:
   emissions_tidy_df[col] = emissions_tidy_df[col].str.strip()

# -------  SAVE CLEAN DATA ------- 

# IAC assess clean data
iac_assess_tidy_df.to_csv("data/intermediate_data/iac_assess_tidy.csv", index=False)
# IAC recc clean data
iac_recc_tidy_df.to_csv("data/intermediate_data/iac_recc_tidy.csv", index=False)
# PPI clean data
ppi_tidy_df.to_csv("data/intermediate_data/ppi_tidy.csv", index=False)
# Generation clean data
generation_df.to_csv("data/intermediate_data/generation.csv", index=False)
# Emissions clean data
emissions_tidy_df.to_csv("data/intermediate_data/emissions_tidy.csv", index=False)