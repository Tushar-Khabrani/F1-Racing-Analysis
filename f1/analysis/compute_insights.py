import pandas as pd
import numpy as np
from pathlib import Path

root = Path(r"c:\Users\Tushar\OneDrive\Desktop\f1")

# Load CSVs with Latin-1 encoding for safety
circuits = pd.read_csv(root / 'circuits.csv', encoding='latin1', engine='python')
constructors = pd.read_csv(root / 'constructors.csv', encoding='latin1', engine='python')
constructor_standings = pd.read_csv(root / 'constructor_standings.csv', encoding='latin1', engine='python')
drivers = pd.read_csv(root / 'drivers.csv', encoding='latin1', engine='python')
driver_standings = pd.read_csv(root / 'driver_standings.csv', encoding='latin1', engine='python')
qualifying = pd.read_csv(root / 'qualifying.csv', encoding='latin1', engine='python')
races = pd.read_csv(root / 'races.csv', encoding='latin1', engine='python')
results = pd.read_csv(root / 'results.csv', encoding='latin1', engine='python')

# Normalize numeric columns
for c in ['position', 'position_order', 'grid', 'points', 'wins', 'q1', 'q2', 'q3']:
    if c in results.columns:
        results[c] = pd.to_numeric(results[c], errors='coerce')
if 'position' in qualifying.columns:
    qualifying['position'] = pd.to_numeric(qualifying['position'], errors='coerce')

# Top driver career metrics
results['podium'] = results['position_order'].isin([1, 2, 3])
results['win'] = results['position_order'] == 1
career = results.groupby('driver_id').agg(
    races=('race_id', 'count'),
    points=('points', 'sum'),
    wins=('win', 'sum'),
    podiums=('podium', 'sum'),
).reset_index()
career = career.merge(drivers[['driver_id', 'givenName', 'familyName', 'nationality']], on='driver_id', how='left')
career['driver'] = career['givenName'].fillna('') + ' ' + career['familyName'].fillna('')
career.sort_values('points', ascending=False, inplace=True)

# Season champions and season trends
final_standings = driver_standings[driver_standings['round'] == driver_standings.groupby('season')['round'].transform('max')]
season_champs = final_standings[final_standings['position'] == 1].copy()
season_champs = season_champs.merge(drivers[['driver_id', 'givenName', 'familyName']], on='driver_id', how='left')
season_champs['driver'] = season_champs['givenName'].fillna('') + ' ' + season_champs['familyName'].fillna('')

# Merge season into results for reliable season-level aggregation
results = results.merge(races[['race_id','season']], on='race_id', how='left')

season_summary = results.groupby('season').agg(
    total_starts=('race_id', 'count'),
    points=('points', 'sum'),
    drivers=('driver_id', 'nunique')
).reset_index()
season_summary = season_summary.merge(
    races.groupby('season')['race_id'].nunique().rename('total_races').reset_index(),
    on='season', how='left'
)
season_summary['dnf_rate'] = (
    results[~results['status'].str.contains('Finished', na=False)]
    .groupby('season')['race_id'].count()
    / results.groupby('season')['race_id'].count()
) * 100
season_summary['dnf_rate'] = season_summary['dnf_rate'].fillna(0)
season_summary = season_summary.sort_values('season')
season_summary['avg_pts'] = season_summary['points'] / season_summary['total_races']

# Win ratios
win_ratio = career[career['races'] >= 50].copy()
win_ratio['ratio'] = 100 * win_ratio['wins'] / win_ratio['races']
win_ratio.sort_values('ratio', ascending=False, inplace=True)

# Consistency
results['finish_pos'] = results['position_order']
consistent = results.groupby('driver_id').agg(
    races=('finish_pos', 'count'),
    avg_finish=('finish_pos', 'mean'),
    best=('finish_pos', 'min'),
    worst=('finish_pos', 'max'),
    finish_rate=('finish_pos', lambda x: x.notna().mean() * 100),
).reset_index()
consistent = consistent[consistent['races'] >= 50].sort_values('avg_finish')
consistent = consistent.merge(drivers[['driver_id', 'givenName', 'familyName', 'nationality']], on='driver_id', how='left')
consistent['driver'] = consistent['givenName'].fillna('') + ' ' + consistent['familyName'].fillna('')

# DNF analysis
dnf = results[~results['status'].str.contains('Finished', na=False)].groupby('driver_id').agg(dnfs=('race_id','count')).reset_index()
driver_race_counts = results.groupby('driver_id')['race_id'].count().rename('races')
driver_finish_rate = results.groupby('driver_id').apply(lambda d: 100 * d['status'].str.contains('Finished', na=False).mean()).rename('finish_rate')
dnf_drivers = dnf.merge(driver_race_counts, on='driver_id').merge(driver_finish_rate, on='driver_id')
dnf_drivers = dnf_drivers.merge(drivers[['driver_id','givenName','familyName','nationality']], on='driver_id', how='left')
dnf_drivers['driver'] = dnf_drivers['givenName'].fillna('') + ' ' + dnf_drivers['familyName'].fillna('')
dnf_drivers.sort_values('dnfs', ascending=False, inplace=True)

# Comebacks
valid_comeback = results.dropna(subset=['grid', 'finish_pos'])
valid_comeback['gain'] = valid_comeback['grid'] - valid_comeback['finish_pos']
comeback = valid_comeback.groupby('driver_id').agg(
    avg_gained=('gain', 'mean'),
    comeback_races=('gain', lambda x: (x > 0).sum()),
    best_comeback=('gain', 'max'),
).reset_index()
comeback = comeback.merge(drivers[['driver_id','givenName','familyName','nationality']], on='driver_id', how='left')
comeback['driver'] = comeback['givenName'].fillna('') + ' ' + comeback['familyName'].fillna('')
comeback.sort_values('avg_gained', ascending=False, inplace=True)

# Qualifying and poles
pole_data = qualifying[qualifying['position'] == 1]
poles = pole_data.groupby('driver_id').size().rename('poles').reset_index()
if 'constructor_id' in qualifying.columns:
    poles['front_row'] = qualifying[qualifying['position'].isin([1,2])].groupby('driver_id').size().reindex(poles['driver_id']).fillna(0).astype(int).values
    poles['q3'] = qualifying[~qualifying['q3'].isna()].groupby('driver_id').size().reindex(poles['driver_id']).fillna(0).astype(int).values
poles = poles.merge(drivers[['driver_id','givenName','familyName','nationality']], on='driver_id', how='left')
poles['driver'] = poles['givenName'].fillna('') + ' ' + poles['familyName'].fillna('')
poles.sort_values('poles', ascending=False, inplace=True)

# Pole-to-win conversion
qualified = qualifying[qualifying['position'] == 1][['race_id','driver_id','constructor_id']]
converted = results[(results['grid'] == 1) & (results['position_order'] == 1)][['race_id','driver_id','constructor_id']]
merged_conv = qualified.merge(converted, on=['race_id','driver_id','constructor_id'], how='inner')
conv = merged_conv.groupby('driver_id').size().rename('converted').reset_index()
conv = qualified.groupby('driver_id').size().rename('total_poles').reset_index().merge(conv, on='driver_id', how='left')
conv['converted'] = conv['converted'].fillna(0)
conv['conv_pct'] = 100 * conv['converted'] / conv['total_poles']
conv = conv.merge(drivers[['driver_id','givenName','familyName']], on='driver_id', how='left')
conv['driver'] = conv['givenName'].fillna('') + ' ' + conv['familyName'].fillna('')
conv.sort_values('conv_pct', ascending=False, inplace=True)

# Constructors
constructor_results = results.groupby('constructor_id').agg(
    races=('race_id', 'count'),
    points=('points', 'sum'),
    wins=('win', 'sum'),
    finishes=('status', lambda x: x.str.contains('Finished', na=False).sum()),
).reset_index()
constructor_results['reliability'] = 100 * constructor_results['finishes'] / constructor_results['races']
constructor_results['avg_pts'] = constructor_results['points'] / constructor_results['races']
constructor_results = constructor_results.merge(constructors[['constructor_id', 'name', 'nationality']], on='constructor_id', how='left')
constructor_results.sort_values('points', ascending=False, inplace=True)

# Constructor nationality
constructor_nation = constructor_results.groupby('nationality').agg(
    constructors=('constructor_id','nunique'),
    points=('points','sum'),
    wins=('wins','sum'),
).reset_index()
constructor_nation.sort_values('points', ascending=False, inplace=True)

# Driver nationality dominance
driver_nation = career.groupby('nationality').agg(
    drivers=('driver_id','count'),
    points=('points','sum'),
    wins=('wins','sum'),
    podiums=('podiums','sum'),
).reset_index().sort_values('points', ascending=False)

# Circuit analysis
circuit_race_counts = races.groupby('circuit_id').size().rename('hosted').reset_index()
for col in ['name', 'country']:
    circuit_race_counts = circuit_race_counts.merge(circuits[['circuit_id', col]], on='circuit_id', how='left')

race_seasons = races.set_index('race_id')['season']
results['season'] = results['race_id'].map(race_seasons)
results['circuit_id'] = results['race_id'].map(races.set_index('race_id')['circuit_id'])

circuit_dnf = results.groupby('circuit_id').agg(
    dnfs=('status', lambda x: (~x.str.contains('Finished', na=False)).sum()),
    total=('race_id','count'),
).reset_index()
circuit_dnf['dnf_rate'] = 100 * circuit_dnf['dnfs'] / circuit_dnf['total']
circuit_dnf = circuit_dnf.merge(circuits[['circuit_id', 'name', 'country']], on='circuit_id', how='left')
circuit_dnf.sort_values('dnf_rate', ascending=False, inplace=True)

circuit_retired = races.groupby('circuit_id').agg(
    first_year=('season', 'min'),
    last_year=('season', 'max'),
    hosted=('race_id','count'),
).reset_index()
circuit_retired = circuit_retired[circuit_retired['last_year'] < 2000]
circuit_retired = circuit_retired.merge(circuits[['circuit_id','name','country']], on='circuit_id', how='left')

# Veterans
veterans = career[career['races'] >= 100].sort_values('races', ascending=False)

# Top 5 constructors for season trends
top5_constructors = constructor_results.head(5)['constructor_id'].tolist()
constructor_season = results[results['constructor_id'].isin(top5_constructors)].groupby(['constructor_id','season'])['points'].sum().reset_index()
constructor_season = constructor_season.merge(constructors[['constructor_id','name']], on='constructor_id', how='left')

# Data quality summary
validation = {
    'table': [],
    'raw_count': [],
    'duplicates_removed': [],
    'null_keys': [],
}
for name, df, keys in [
    ('drivers', drivers, ['driver_id']),
    ('constructors', constructors, ['constructor_id']),
    ('circuits', circuits, ['circuit_id']),
    ('races', races, ['race_id']),
    ('results', results, ['race_id','driver_id','constructor_id']),
    ('qualifying', qualifying, ['race_id','driver_id']),
    ('driver_standings', driver_standings, ['season','round','driver_id']),
    ('constructor_standings', constructor_standings, ['season','round','constructor_id']),
]:
    raw = len(df)
    dup = raw - len(df.drop_duplicates(subset=keys))
    nulls = df[keys].isna().any(axis=1).sum()
    validation['table'].append(name)
    validation['raw_count'].append(raw)
    validation['duplicates_removed'].append(dup)
    validation['null_keys'].append(nulls)

# Print insights
print('=== TOP 10 DRIVERS BY CAREER POINTS ===')
print(career[['driver','nationality','points','wins','podiums','races']].head(10).to_string(index=False))
print()
print('=== TOP 10 SEASON CHAMPIONS ===')
print(season_champs[['season','driver','points','wins']].sort_values('season').head(10).to_string(index=False))
print()
print('=== TOP WIN RATIOS (50+ RACES) ===')
print(win_ratio[['driver','nationality','wins','races','ratio']].head(10).to_string(index=False, float_format='%.1f'))
print()
print('=== MOST CONSISTENT DRIVERS (50+ RACES) ===')
print(consistent[['driver','nationality','races','avg_finish','finish_rate']].head(10).to_string(index=False, float_format='%.2f'))
print()
print('=== MOST DNFs ===')
print(dnf_drivers[['driver','nationality','dnfs','races','finish_rate']].head(10).to_string(index=False, float_format='%.1f'))
print()
print('=== BEST COME BACKS ===')
print(comeback[['driver','nationality','avg_gained','best_comeback','comeback_races']].head(10).to_string(index=False, float_format='%.2f'))
print()
print('=== TOP POLE DRIVERS ===')
print(poles[['driver','nationality','poles','front_row','q3']].head(10).to_string(index=False))
print()
print('=== POLE-TO-WIN CONVERSION ===')
print(conv[['driver','total_poles','converted','conv_pct']].head(10).to_string(index=False, float_format='%.1f'))
print()
print('=== TOP 10 CONSTRUCTORS ===')
print(constructor_results[['name','nationality','points','wins','reliability','avg_pts']].head(10).to_string(index=False, float_format='%.2f'))
print()
print('=== CONSTRUCTOR NATIONALITY DOMINANCE ===')
print(constructor_nation.head(10).to_string(index=False, float_format='%.1f'))
print()
print('=== DRIVER NATIONALITY DOMINANCE ===')
print(driver_nation.head(10).to_string(index=False, float_format='%.1f'))
print()
print('=== TOP CIRCUITS BY RACES HOSTED ===')
print(circuit_race_counts.sort_values('hosted', ascending=False).head(10).to_string(index=False))
print()
print('=== CIRCUITS WITH HIGHEST DNF RATE ===')
print(circuit_dnf[['name','country','dnf_rate','dnfs','total']].head(10).to_string(index=False, float_format='%.1f'))
print()
print('=== RETIRED CIRCUITS BEFORE 2000 ===')
print(circuit_retired.sort_values('last_year', ascending=False).head(10).to_string(index=False))
print()
print('=== SEASON TRENDS ===')
print(season_summary[['season','total_races','drivers','points','dnf_rate','avg_pts']].head(10).to_string(index=False, float_format='%.2f'))
print()
print('=== DATA VALIDATION SUMMARY ===')
print(pd.DataFrame(validation).to_string(index=False))
print()
print('=== TOP 5 CONSTRUCTOR SEASON TREND SAMPLE ===')
print(constructor_season.sort_values(['season','constructor_id']).head(20).to_string(index=False))
