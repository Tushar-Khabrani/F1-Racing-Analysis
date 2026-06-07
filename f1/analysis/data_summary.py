import pandas as pd
from pathlib import Path
root = Path(r"c:\Users\Tushar\OneDrive\Desktop\f1")
races = pd.read_csv(root / 'races.csv', encoding='latin1', engine='python')
results = pd.read_csv(root / 'results.csv', encoding='latin1', engine='python')
print('total_races_csv', len(races))
print('season_min', races['season'].min())
print('season_max', races['season'].max())
print('year_min', races['season'].astype(int).min())
print('year_max', races['season'].astype(int).max())
print('total_result_rows', len(results))
print('result_duplicates_all_cols', len(results) - len(results.drop_duplicates(subset=['race_id','driver_id','constructor_id','grid','position'])))
print('result_duplicates_key_cols', len(results) - len(results.drop_duplicates(subset=['race_id','driver_id','constructor_id'])))
