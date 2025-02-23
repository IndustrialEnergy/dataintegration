import pandas as pd
from pathlib import Path
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np


# import data
# ------- define paths -------
# define relative path
relative_path = Path('../data/raw_data/')

# get absolute path
absolute_path = relative_path.resolve()
#print(absolute_path)

# declare file names
filename_iac = "IAC_Database_20250208.xls"

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


# ------- generate a dataframe with NULL NAICS -------

# check missing NAICS codes
print(f'Total count of ARCs with Null NAICS: {iac_assess_df[iac_assess_df["NAICS"].isna()].count()}')

null_naics_df = iac_assess_df[iac_assess_df['NAICS'].isna()]
print(f'Total count of ARCs with Null NAICS per year: {null_naics_df["FY"].value_counts()}')

# filter only energy related ARCs from the recc table
recc_energy_df = iac_recc_df[iac_recc_df['ARC2'].astype(str).str[0] == str('2')]

# generate a dataframe with NULL NAICS values for all assessments IDs that have recommendations within an Energy section
null_naics_energy_df = null_naics_df[null_naics_df['ID'].isin(recc_energy_df['ID'])]

# export the dataframe
null_naics_energy_df.to_csv("../data/intermediate_data/null_naics_v3.csv", index=False)