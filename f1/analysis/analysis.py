import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
import warnings
os.makedirs("./graphs", exist_ok=True)
warnings.filterwarnings('ignore')

plt.rcParams['figure.dpi'] = 150
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

F1_RED    = '#E8002D'
F1_DARK   = '#15151E'
F1_SILVER = '#C0C0C0'
F1_GOLD   = '#FFD700'
F1_WHITE  = '#FFFFFF'
ACCENT    = '#FF8700'

def q(sql):
    conn = mysql.connector.connect(host='localhost', user='root', password='Tush@rK104', database='f1_analysis')
    df = pd.read_sql(sql, conn)
    conn.close()
    return df

def save(fig, name):
    fig.savefig(f'./graphs/{name}.png', bbox_inches='tight', facecolor=F1_DARK, edgecolor='none')
    plt.close(fig)
    print(f'Saved: {name}.png')

top_drivers = q("SELECT entity_name, metric1_value races, metric2_value points, metric3_value wins, metric4_value podiums, extra_info nat FROM master_insights WHERE insight_name='Top Drivers All Time by Points' ORDER BY rank_no")
season_winners = q("SELECT season, entity_name driver, metric1_value points, metric2_value wins, metric3_value podiums FROM master_insights WHERE insight_name='Best Driver Per Season' ORDER BY season")
dnf_drivers = q("SELECT entity_name, metric1_value dnfs, metric2_value finish_rate, metric3_value races, extra_info nat FROM master_insights WHERE insight_name='Drivers With Most DNFs' ORDER BY rank_no LIMIT 15")
veterans = q("SELECT entity_name, metric1_value races, metric2_value points, metric3_value wins, extra_info nat FROM master_insights WHERE insight_name='Veteran Drivers 100+ Races' ORDER BY rank_no LIMIT 15")
comeback = q("SELECT entity_name, metric1_value avg_gained, metric2_value comeback_races, metric3_value best_comeback, extra_info nat FROM master_insights WHERE insight_name='Driver Comeback Performance' ORDER BY rank_no LIMIT 15")
consistent = q("SELECT entity_name, metric1_value avg_finish, metric2_value best, metric3_value worst, metric4_value finish_rate, extra_info nat FROM master_insights WHERE insight_name='Most Consistent Drivers' ORDER BY rank_no LIMIT 15")
win_ratio = q("SELECT entity_name, metric1_value ratio, metric2_value wins, metric3_value races, extra_info nat FROM master_insights WHERE insight_name='Top Win Ratio min50 Races' ORDER BY rank_no")
poles = q("SELECT entity_name, metric1_value poles, metric2_value pole_pct, metric3_value front_row, metric4_value q3, extra_info nat FROM master_insights WHERE insight_name='Most Pole Positions All Time' ORDER BY rank_no")
pole_conversion = q("SELECT entity_name, metric1_value converted, metric2_value total_poles, metric3_value conv_pct FROM master_insights WHERE insight_name='Poles Converted to Wins' ORDER BY rank_no LIMIT 10")
grid_improvers = q("SELECT entity_name, metric1_value avg_gained, metric2_value races_improved, metric3_value poles, extra_info nat FROM master_insights WHERE insight_name='Best Grid to Race Improvers' ORDER BY rank_no LIMIT 15")
constructors_all = q("SELECT entity_name, metric1_value points, metric2_value wins, metric3_value reliability, metric4_value avg_pts, extra_info nat FROM master_insights WHERE insight_name='Constructor All Time Performance' ORDER BY rank_no LIMIT 15")
constructor_rel = q("SELECT entity_name, metric1_value rel_pct, metric2_value dnfs, metric3_value points, metric4_value wins, extra_info nat FROM master_insights WHERE insight_name='Constructor Reliability Ranking' ORDER BY rank_no LIMIT 15")
const_nat = q("SELECT entity_name, metric1_value constructors, metric2_value points, metric3_value wins, metric4_value podiums FROM master_insights WHERE insight_name='Constructor Nationality Distribution' ORDER BY rank_no")
circuit_races = q("SELECT entity_name, metric1_value hosted, metric2_value active, metric3_value drivers, metric4_value constructors, extra_info country FROM master_insights WHERE insight_name='Most Races Hosted' ORDER BY rank_no")
difficult_circuits = q("SELECT entity_name, metric1_value dnf_rate, metric2_value dnfs, metric3_value hosted, metric4_value drivers, extra_info country FROM master_insights WHERE insight_name='Most Difficult Circuits High DNF Rate' ORDER BY rank_no")
retired_circuits = q("SELECT entity_name, metric1_value last_year, metric2_value first_year, metric3_value hosted, extra_info country FROM master_insights WHERE insight_name='Retired Circuits Before 2000' ORDER BY rank_no")
season_growth = q("SELECT season, metric1_value total_races, metric2_value drivers, metric3_value points, metric4_value dnf_rate FROM master_insights WHERE insight_name='Season Growth Trend' ORDER BY season")
season_dnf = q("SELECT season, metric1_value dnf_rate, metric2_value dnfs, metric3_value races, metric4_value drivers FROM master_insights WHERE insight_name='Season Highest DNF Rate' ORDER BY rank_no")
season_avg_pts = q("SELECT season, metric1_value avg_pts, metric2_value races, metric3_value total_pts FROM master_insights WHERE insight_name='Avg Points Per Race Per Season' ORDER BY season")
nat_dom = q("SELECT entity_name, metric1_value drivers, metric2_value points, metric3_value wins, metric4_value podiums FROM master_insights WHERE insight_name='Nationality Dominance' ORDER BY rank_no LIMIT 12")
validation = q("SELECT * FROM validation_checks")

print("Data loaded from master_insights")

# ── GRAPH 1: Top 10 Drivers All Time ──────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 7), facecolor=F1_DARK)
fig.suptitle('TOP 10 DRIVERS — ALL TIME', color=F1_WHITE, fontsize=16, fontweight='bold', y=1.01)
ax = axes[0]
ax.set_facecolor(F1_DARK)
colors = [F1_GOLD, F1_SILVER, '#CD7F32'] + [F1_RED]*7
ax.barh(top_drivers['entity_name'][::-1], top_drivers['points'][::-1], color=colors[::-1], height=0.7)
for i, (val, name) in enumerate(zip(top_drivers['points'][::-1], top_drivers['entity_name'][::-1])):
    ax.text(val+15, i, f'{val:.0f}', va='center', color=F1_WHITE, fontsize=9)
ax.set_xlabel('Total Points', color=F1_SILVER)
ax.set_title('Total Career Points', color=F1_WHITE, fontsize=12)
ax.tick_params(colors=F1_WHITE)
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
ax2 = axes[1]
ax2.set_facecolor(F1_DARK)
x = np.arange(len(top_drivers))
ax2.bar(x-0.18, top_drivers['wins'], 0.35, color=F1_RED, label='Wins')
ax2.bar(x+0.18, top_drivers['podiums'], 0.35, color=ACCENT, label='Podiums')
ax2.set_xticks(x)
ax2.set_xticklabels([n.split()[-1] for n in top_drivers['entity_name']], rotation=45, ha='right', color=F1_WHITE, fontsize=8)
ax2.set_title('Wins vs Podiums', color=F1_WHITE, fontsize=12)
ax2.tick_params(colors=F1_WHITE)
ax2.legend(facecolor=F1_DARK, labelcolor=F1_WHITE)
ax2.spines['bottom'].set_color(F1_SILVER)
ax2.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '01_top_drivers_alltime')

# ── GRAPH 2: Season Champions ─────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(20, 6), facecolor=F1_DARK)
ax.set_facecolor(F1_DARK)
driver_wins = season_winners.groupby('driver')['season'].count().sort_values(ascending=False).head(12)
c = [F1_GOLD if i==0 else F1_RED if i<3 else F1_SILVER for i in range(len(driver_wins))]
ax.bar(driver_wins.index, driver_wins.values, color=c, width=0.6)
for i, (name, val) in enumerate(driver_wins.items()):
    ax.text(i, val+0.1, str(int(val)), ha='center', color=F1_WHITE, fontsize=11, fontweight='bold')
ax.set_title('CHAMPIONSHIPS WON PER DRIVER', color=F1_WHITE, fontsize=14, fontweight='bold')
ax.set_ylabel('Championships', color=F1_SILVER)
ax.tick_params(colors=F1_WHITE)
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '02_season_champions')

# ── GRAPH 3: Season Points Heatmap ────────────────────────────────────────────
pivot = season_winners.pivot_table(index='driver', columns='season', values='points', fill_value=0)
pivot = pivot.loc[pivot.sum(axis=1).sort_values(ascending=False).head(8).index]
fig, ax = plt.subplots(figsize=(24, 6), facecolor=F1_DARK)
ax.set_facecolor(F1_DARK)
im = ax.imshow(pivot.values, aspect='auto', cmap='YlOrRd')
ax.set_yticks(range(len(pivot.index)))
ax.set_yticklabels(pivot.index, color=F1_WHITE, fontsize=9)
ax.set_xticks(range(len(pivot.columns)))
ax.set_xticklabels(pivot.columns.astype(int), rotation=90, color=F1_WHITE, fontsize=7)
ax.set_title('SEASON POINTS HEATMAP — TOP 8 CHAMPIONS', color=F1_WHITE, fontsize=13, fontweight='bold')
cbar = plt.colorbar(im, ax=ax)
cbar.ax.tick_params(colors=F1_WHITE)
cbar.ax.yaxis.label.set_color(F1_WHITE)
fig.patch.set_facecolor(F1_DARK)
save(fig, '03_season_points_heatmap')

# ── GRAPH 4: Win Ratio & Consistency ─────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 7), facecolor=F1_DARK)
fig.suptitle('WIN RATIO & CONSISTENCY', color=F1_WHITE, fontsize=15, fontweight='bold')
ax = axes[0]
ax.set_facecolor(F1_DARK)
ax.barh(win_ratio['entity_name'][::-1], win_ratio['ratio'][::-1], color=F1_RED, height=0.6)
for i, val in enumerate(win_ratio['ratio'][::-1]):
    ax.text(val+0.3, i, f'{val:.1f}%', va='center', color=F1_WHITE, fontsize=9)
ax.set_title('Top Win Ratio (min 50 races)', color=F1_WHITE, fontsize=11)
ax.set_xlabel('Win %', color=F1_SILVER)
ax.tick_params(colors=F1_WHITE)
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
ax2 = axes[1]
ax2.set_facecolor(F1_DARK)
ax2.barh(consistent['entity_name'][::-1], consistent['avg_finish'][::-1], color=ACCENT, height=0.6)
for i, val in enumerate(consistent['avg_finish'][::-1]):
    ax2.text(val+0.05, i, f'{val:.2f}', va='center', color=F1_WHITE, fontsize=9)
ax2.set_title('Most Consistent (avg finish, lower=better)', color=F1_WHITE, fontsize=11)
ax2.set_xlabel('Avg Finish Position', color=F1_SILVER)
ax2.tick_params(colors=F1_WHITE)
ax2.spines['bottom'].set_color(F1_SILVER)
ax2.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '04_win_ratio_consistency')

# ── GRAPH 5: DNFs & Comebacks ─────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 7), facecolor=F1_DARK)
fig.suptitle('DNFs & COMEBACKS', color=F1_WHITE, fontsize=15, fontweight='bold')
ax = axes[0]
ax.set_facecolor(F1_DARK)
ax.barh(dnf_drivers['entity_name'][::-1], dnf_drivers['dnfs'][::-1], color='#FF4444', height=0.65)
ax.set_title('Most DNFs All Time', color=F1_WHITE, fontsize=12)
ax.set_xlabel('DNF Count', color=F1_SILVER)
ax.tick_params(colors=F1_WHITE)
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
ax2 = axes[1]
ax2.set_facecolor(F1_DARK)
ax2.barh(comeback['entity_name'][::-1], comeback['avg_gained'][::-1], color='#00C896', height=0.65)
ax2.axvline(0, color=F1_SILVER, linestyle='--', linewidth=1)
ax2.set_title('Best Comeback (Avg positions gained)', color=F1_WHITE, fontsize=12)
ax2.set_xlabel('Avg Positions Gained', color=F1_SILVER)
ax2.tick_params(colors=F1_WHITE)
ax2.spines['bottom'].set_color(F1_SILVER)
ax2.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '05_dnf_comebacks')

# ── GRAPH 6: Qualifying ───────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 7), facecolor=F1_DARK)
fig.suptitle('QUALIFYING ANALYSIS', color=F1_WHITE, fontsize=15, fontweight='bold')
ax = axes[0]
ax.set_facecolor(F1_DARK)
ax.barh(poles['entity_name'][::-1], poles['poles'][::-1], color=F1_RED, height=0.6)
for i, (val, pct) in enumerate(zip(poles['poles'][::-1], poles['pole_pct'][::-1])):
    ax.text(val+0.3, i, f'{val:.0f}  ({pct:.1f}%)', va='center', color=F1_WHITE, fontsize=9)
ax.set_title('Most Pole Positions All Time', color=F1_WHITE, fontsize=12)
ax.set_xlabel('Poles', color=F1_SILVER)
ax.tick_params(colors=F1_WHITE)
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
ax2 = axes[1]
ax2.set_facecolor(F1_DARK)
ax2.barh(pole_conversion['entity_name'][::-1], pole_conversion['conv_pct'][::-1], color=ACCENT, height=0.6)
for i, val in enumerate(pole_conversion['conv_pct'][::-1]):
    ax2.text(val+0.3, i, f'{val:.1f}%', va='center', color=F1_WHITE, fontsize=9)
ax2.set_title('Pole-to-Win Conversion %', color=F1_WHITE, fontsize=12)
ax2.set_xlabel('Conversion %', color=F1_SILVER)
ax2.tick_params(colors=F1_WHITE)
ax2.spines['bottom'].set_color(F1_SILVER)
ax2.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '06_qualifying_analysis')

# ── GRAPH 7: Grid Improvers ───────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(16, 7), facecolor=F1_DARK)
ax.set_facecolor(F1_DARK)
colors_gi = ['#00C896' if v>0 else '#FF4444' for v in grid_improvers['avg_gained'][::-1]]
ax.barh(grid_improvers['entity_name'][::-1], grid_improvers['avg_gained'][::-1], color=colors_gi, height=0.65)
ax.axvline(0, color=F1_SILVER, linestyle='--', linewidth=1)
ax.set_title('BEST GRID-TO-RACE POSITION GAINERS', color=F1_WHITE, fontsize=14, fontweight='bold')
ax.set_xlabel('Avg Positions Gained from Grid', color=F1_SILVER)
ax.tick_params(colors=F1_WHITE)
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '07_grid_improvers')

# ── GRAPH 8: Constructors ─────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(20, 8), facecolor=F1_DARK)
fig.suptitle('CONSTRUCTORS ALL TIME', color=F1_WHITE, fontsize=15, fontweight='bold')
ax = axes[0]
ax.set_facecolor(F1_DARK)
ax.barh(constructors_all['entity_name'][::-1], constructors_all['points'][::-1], color=F1_RED, height=0.65)
for i, val in enumerate(constructors_all['points'][::-1]):
    ax.text(val+10, i, f'{val:.0f}', va='center', color=F1_WHITE, fontsize=8)
ax.set_title('Total Points', color=F1_WHITE, fontsize=12)
ax.set_xlabel('Points', color=F1_SILVER)
ax.tick_params(colors=F1_WHITE)
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
ax2 = axes[1]
ax2.set_facecolor(F1_DARK)
ax2.barh(constructor_rel['entity_name'][::-1], constructor_rel['rel_pct'][::-1], color='#00C896', height=0.65)
for i, val in enumerate(constructor_rel['rel_pct'][::-1]):
    ax2.text(val+0.2, i, f'{val:.1f}%', va='center', color=F1_WHITE, fontsize=9)
ax2.set_title('Reliability % (top 15)', color=F1_WHITE, fontsize=12)
ax2.set_xlabel('Reliability %', color=F1_SILVER)
ax2.set_xlim(0, 115)
ax2.tick_params(colors=F1_WHITE)
ax2.spines['bottom'].set_color(F1_SILVER)
ax2.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '08_constructors_alltime')

# ── GRAPH 9: Nationality Pie Charts ───────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(18, 7), facecolor=F1_DARK)
fig.suptitle('NATIONALITY DOMINANCE', color=F1_WHITE, fontsize=15, fontweight='bold')
ax = axes[0]
ax.set_facecolor(F1_DARK)
cmap1 = plt.cm.Set1(np.linspace(0, 1, len(const_nat)))
wedges, texts, autotexts = ax.pie(const_nat['points'], labels=const_nat['entity_name'],
                                   autopct='%1.1f%%', colors=cmap1,
                                   textprops={'color': F1_WHITE, 'fontsize': 8})
for at in autotexts:
    at.set_color(F1_DARK); at.set_fontsize(7)
ax.set_title('Constructor Points by Nationality', color=F1_WHITE, fontsize=11)
ax2 = axes[1]
ax2.set_facecolor(F1_DARK)
cmap2 = plt.cm.tab20(np.linspace(0, 1, len(nat_dom)))
wedges2, texts2, autotexts2 = ax2.pie(nat_dom['points'], labels=nat_dom['entity_name'],
                                       autopct='%1.1f%%', colors=cmap2,
                                       textprops={'color': F1_WHITE, 'fontsize': 8})
for at in autotexts2:
    at.set_color(F1_DARK); at.set_fontsize(7)
ax2.set_title('Driver Points by Nationality', color=F1_WHITE, fontsize=11)
fig.patch.set_facecolor(F1_DARK)
save(fig, '09_nationality_dominance')

# ── GRAPH 10: Circuits ────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(20, 8), facecolor=F1_DARK)
fig.suptitle('CIRCUIT ANALYSIS', color=F1_WHITE, fontsize=15, fontweight='bold')
ax = axes[0]
ax.set_facecolor(F1_DARK)
ax.barh(circuit_races['entity_name'][::-1], circuit_races['hosted'][::-1], color=ACCENT, height=0.65)
for i, (val, cty) in enumerate(zip(circuit_races['hosted'][::-1], circuit_races['country'][::-1])):
    ax.text(val+0.2, i, f'{val:.0f}  {cty}', va='center', color=F1_WHITE, fontsize=8)
ax.set_title('Most Races Hosted', color=F1_WHITE, fontsize=12)
ax.set_xlabel('Races', color=F1_SILVER)
ax.tick_params(colors=F1_WHITE)
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
ax2 = axes[1]
ax2.set_facecolor(F1_DARK)
ax2.barh(difficult_circuits['entity_name'][::-1], difficult_circuits['dnf_rate'][::-1], color='#FF4444', height=0.65)
for i, (val, cty) in enumerate(zip(difficult_circuits['dnf_rate'][::-1], difficult_circuits['country'][::-1])):
    ax2.text(val+0.2, i, f'{val:.1f}%  {cty}', va='center', color=F1_WHITE, fontsize=8)
ax2.set_title('Highest DNF Rate Circuits', color=F1_WHITE, fontsize=12)
ax2.set_xlabel('DNF Rate %', color=F1_SILVER)
ax2.tick_params(colors=F1_WHITE)
ax2.spines['bottom'].set_color(F1_SILVER)
ax2.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '10_circuits_analysis')

# ── GRAPH 11: Retired Circuits ────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(16, 7), facecolor=F1_DARK)
ax.set_facecolor(F1_DARK)
ax.barh(retired_circuits['entity_name'][::-1], retired_circuits['hosted'][::-1], color=F1_SILVER, height=0.6)
for i, row in retired_circuits[::-1].reset_index(drop=True).iterrows():
    ax.text(row['hosted']+0.1, i, f"{row['country']}  {int(row['first_year'])}-{int(row['last_year'])}",
            va='center', color=F1_WHITE, fontsize=8)
ax.set_title('RETIRED CIRCUITS (Last Used Before 2000)', color=F1_WHITE, fontsize=13, fontweight='bold')
ax.set_xlabel('Races Hosted', color=F1_SILVER)
ax.tick_params(colors=F1_WHITE)
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '11_retired_circuits')

# ── GRAPH 12: Season Trends (4 plots) ────────────────────────────────────────
fig, axes = plt.subplots(2, 2, figsize=(20, 12), facecolor=F1_DARK)
fig.suptitle('SEASON TRENDS OVER TIME', color=F1_WHITE, fontsize=16, fontweight='bold')
pairs = [
    (axes[0][0], 'total_races', F1_RED, 'Races Per Season'),
    (axes[0][1], 'drivers', ACCENT, 'Unique Drivers Per Season'),
    (axes[1][0], 'points', '#00C896', 'Total Points Awarded Per Season'),
    (axes[1][1], 'dnf_rate', '#FF4444', 'DNF Rate % Per Season'),
]
for ax_i, col, color, title in pairs:
    ax_i.set_facecolor(F1_DARK)
    ax_i.plot(season_growth['season'], season_growth[col], color=color, linewidth=2, marker='o', markersize=2)
    ax_i.fill_between(season_growth['season'], season_growth[col], alpha=0.15, color=color)
    ax_i.set_title(title, color=F1_WHITE, fontsize=11)
    ax_i.set_xlabel('Season', color=F1_SILVER)
    ax_i.tick_params(colors=F1_WHITE)
    ax_i.spines['bottom'].set_color(F1_SILVER)
    ax_i.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '12_season_trends')

# ── GRAPH 13: Avg Points Per Season ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(18, 6), facecolor=F1_DARK)
ax.set_facecolor(F1_DARK)
ax.bar(season_avg_pts['season'], season_avg_pts['avg_pts'], color=F1_RED, width=0.8)
z = np.polyfit(season_avg_pts['season'].astype(float), season_avg_pts['avg_pts'].astype(float), 1)
p = np.poly1d(z)
ax.plot(season_avg_pts['season'], p(season_avg_pts['season'].astype(float)), color=F1_GOLD, linewidth=2, linestyle='--', label='Trend')
ax.set_title('AVG POINTS PER RACE PER SEASON', color=F1_WHITE, fontsize=14, fontweight='bold')
ax.set_xlabel('Season', color=F1_SILVER)
ax.set_ylabel('Avg Points', color=F1_SILVER)
ax.tick_params(colors=F1_WHITE)
ax.legend(facecolor=F1_DARK, labelcolor=F1_WHITE)
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '13_avg_points_per_season')

# ── GRAPH 14: Worst DNF Seasons ───────────────────────────────────────────────
season_dnf_s = season_dnf.sort_values('dnf_rate', ascending=False).head(15)
fig, ax = plt.subplots(figsize=(14, 6), facecolor=F1_DARK)
ax.set_facecolor(F1_DARK)
bars = ax.bar(season_dnf_s['season'].astype(str), season_dnf_s['dnf_rate'], color='#FF4444', width=0.7)
for bar, val in zip(bars, season_dnf_s['dnf_rate']):
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.3, f'{val:.1f}%', ha='center', color=F1_WHITE, fontsize=8)
ax.set_title('TOP 15 SEASONS BY DNF RATE', color=F1_WHITE, fontsize=14, fontweight='bold')
ax.set_xlabel('Season', color=F1_SILVER)
ax.set_ylabel('DNF Rate %', color=F1_SILVER)
ax.tick_params(colors=F1_WHITE)
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '14_season_dnf_rates')

# ── GRAPH 15: Data Validation ─────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 6), facecolor=F1_DARK)
ax.set_facecolor(F1_DARK)
x = np.arange(len(validation))
ax.bar(x - 0.2, validation['raw_count'], 0.38, color=F1_SILVER, label='Raw Count')
ax.bar(x + 0.2, validation['clean_count'], 0.38, color=F1_RED, label='Clean Count')
ax.set_xticks(x)
ax.set_xticklabels(validation['table_name'], rotation=30, ha='right', color=F1_WHITE, fontsize=9)
ax.set_title('DATA QUALITY — RAW vs CLEAN ROW COUNTS', color=F1_WHITE, fontsize=13, fontweight='bold')
ax.set_ylabel('Row Count', color=F1_SILVER)
ax.tick_params(colors=F1_WHITE)
ax.legend(facecolor=F1_DARK, labelcolor=F1_WHITE)
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '15_data_quality')

# ── GRAPH 16: Scatter - Races vs Points ──────────────────────────────────────
driver_full = q("SELECT driver_name, races_participated, total_points, wins, nationality FROM driver_analysis WHERE races_participated >= 20")
fig, ax = plt.subplots(figsize=(14, 8), facecolor=F1_DARK)
ax.set_facecolor(F1_DARK)
sc = ax.scatter(driver_full['races_participated'], driver_full['total_points'],
                c=driver_full['wins'], cmap='YlOrRd', s=60, alpha=0.7, edgecolors='none')
cbar = plt.colorbar(sc, ax=ax)
cbar.ax.tick_params(colors=F1_WHITE)
cbar.set_label('Wins', color=F1_WHITE)
top10 = driver_full.nlargest(10, 'total_points')
for _, row in top10.iterrows():
    ax.annotate(row['driver_name'].split()[-1], (row['races_participated'], row['total_points']),
                textcoords='offset points', xytext=(5, 5), color=F1_WHITE, fontsize=7)
ax.set_title('RACES PARTICIPATED vs TOTAL POINTS (colored by wins)', color=F1_WHITE, fontsize=13, fontweight='bold')
ax.set_xlabel('Races Participated', color=F1_SILVER)
ax.set_ylabel('Total Points', color=F1_SILVER)
ax.tick_params(colors=F1_WHITE)
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '16_races_vs_points_scatter')

# ── GRAPH 17: Veteran Drivers ─────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 7), facecolor=F1_DARK)
ax.set_facecolor(F1_DARK)
ax.barh(veterans['entity_name'][::-1], veterans['races'][::-1], color=ACCENT, height=0.65)
ax2_twin = ax.twiny()
ax2_twin.barh(veterans['entity_name'][::-1], veterans['points'][::-1], color='none', height=0)
for i, (r, p, w) in enumerate(zip(veterans['races'][::-1], veterans['points'][::-1], veterans['wins'][::-1])):
    ax.text(r+0.5, i, f'{r:.0f} races  |  {p:.0f} pts  |  {w:.0f} wins', va='center', color=F1_WHITE, fontsize=8)
ax.set_title('VETERAN DRIVERS — 100+ RACES', color=F1_WHITE, fontsize=14, fontweight='bold')
ax.set_xlabel('Races Participated', color=F1_SILVER)
ax.tick_params(colors=F1_WHITE)
ax2_twin.tick_params(colors=F1_WHITE)
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
ax2_twin.spines['top'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '17_veteran_drivers')

# ── GRAPH 18: Constructor Season Dominance ────────────────────────────────────
const_dom = q("SELECT season, entity_name, metric1_value points FROM master_insights WHERE insight_name='Constructor Dominance By Season' AND rank_no=1 ORDER BY season")
top5_const = q("SELECT entity_name FROM master_insights WHERE insight_name='Constructor All Time Performance' GROUP BY entity_name ORDER BY MIN(rank_no) LIMIT 5")
top5_list = list(top5_const['entity_name'])
const_season_pts = q(f"""
    SELECT season, entity_name, metric1_value points FROM master_insights
    WHERE insight_name='Constructor Dominance By Season'
    AND entity_name IN ({','.join([chr(39)+c+chr(39) for c in top5_list])})
    ORDER BY season
""")
pivot2 = const_season_pts.pivot_table(index='entity_name', columns='season', values='points', fill_value=0)
fig, ax = plt.subplots(figsize=(22, 5), facecolor=F1_DARK)
ax.set_facecolor(F1_DARK)
colors_line = [F1_RED, ACCENT, F1_GOLD, '#00C896', F1_SILVER]
for i, (idx, row) in enumerate(pivot2.iterrows()):
    ax.plot(pivot2.columns, row.values, color=colors_line[i], linewidth=2, label=idx, marker='o', markersize=2)
ax.set_title('TOP 5 CONSTRUCTOR POINTS PER SEASON', color=F1_WHITE, fontsize=13, fontweight='bold')
ax.set_xlabel('Season', color=F1_SILVER)
ax.set_ylabel('Points', color=F1_SILVER)
ax.tick_params(colors=F1_WHITE)
ax.legend(facecolor=F1_DARK, labelcolor=F1_WHITE, loc='upper left')
ax.spines['bottom'].set_color(F1_SILVER)
ax.spines['left'].set_color(F1_SILVER)
fig.patch.set_facecolor(F1_DARK)
save(fig, '18_constructor_season_trends')

print("\nAll 18 graphs saved successfully!")


SEP = "=" * 70

def header(title):
    print(f"\n{SEP}")
    print(f"  {title}")
    print(SEP)

def subheader(title):
    print(f"\n  --- {title} ---")

print("\n\n")
print("=" * 70)
print("        F1 COMPLETE ANALYTICS & INSIGHTS REPORT")
print("=" * 70)


header("1. TOP 10 DRIVERS — ALL TIME BY POINTS")
for i, row in top_drivers.iterrows():
    print(f"  #{int(row['rank_no']) if 'rank_no' in top_drivers.columns else i+1}  {row['entity_name']:<25}  Points: {row['points']:>8.1f}  Wins: {row['wins']:>4.0f}  Podiums: {row['podiums']:>4.0f}  ({row['nat']})")

subheader("KEY INSIGHTS")
best = top_drivers.iloc[0]
print(f"  * {best['entity_name']} leads all time with {best['points']:.0f} points and {best['wins']:.0f} wins")
print(f"  * Top 3 combined points: {top_drivers.head(3)['points'].sum():.0f}")
avg_wins = top_drivers['wins'].mean()
print(f"  * Avg wins among top 10: {avg_wins:.1f}")


header("2. SEASON CHAMPIONS")
champ_count = season_winners.groupby('driver')['season'].count().sort_values(ascending=False)
print(f"\n  {'Driver':<25} Championships   Seasons")
print(f"  {'-'*50}")
for driver, count in champ_count.head(10).items():
    seasons_list = sorted(season_winners[season_winners['driver']==driver]['season'].tolist())
    seasons_str = ', '.join(map(str, seasons_list[:5])) + ('...' if len(seasons_list)>5 else '')
    print(f"  {driver:<25} {count:>3}           {seasons_str}")

subheader("KEY INSIGHTS")
print(f"  * {champ_count.index[0]} is most decorated with {champ_count.iloc[0]} championships")
print(f"  * {len(champ_count)} unique champions across {season_winners['season'].nunique()} seasons")
multi = (champ_count > 1).sum()
print(f"  * {multi} drivers won more than 1 championship")
print(f"  * Latest season in data: {int(season_winners['season'].max())} — Champion: {season_winners[season_winners['season']==season_winners['season'].max()]['driver'].values[0]}")


header("3. WIN RATIO — DRIVERS WITH MIN 50 RACES")
print(f"\n  {'Driver':<25} Win%    Wins  Races  Podium%  ({' '}Nationality)")
print(f"  {'-'*65}")
for _, row in win_ratio.iterrows():
    print(f"  {row['entity_name']:<25} {row['ratio']:>5.1f}%  {row['wins']:>4.0f}  {row['races']:>5.0f}  ({row['nat']})")

subheader("KEY INSIGHTS")
print(f"  * {win_ratio.iloc[0]['entity_name']} has highest win ratio: {win_ratio.iloc[0]['ratio']:.1f}%")
print(f"  * Only {len(win_ratio)} drivers achieved >0% win rate in 50+ races")


header("4. MOST CONSISTENT DRIVERS")
print(f"\n  {'Driver':<25} Avg Finish  Best  Worst  Finish Rate%")
print(f"  {'-'*60}")
for _, row in consistent.head(10).iterrows():
    print(f"  {row['entity_name']:<25} {row['avg_finish']:>6.2f}      {row['best']:>3.0f}   {row['worst']:>4.0f}   {row['finish_rate']:>5.1f}%")

subheader("KEY INSIGHTS")
print(f"  * {consistent.iloc[0]['entity_name']} most consistent — avg finish pos: {consistent.iloc[0]['avg_finish']:.2f}")
print(f"  * {consistent.iloc[0]['entity_name']} finish rate: {consistent.iloc[0]['finish_rate']:.1f}%")


header("5. DNF ANALYSIS")
print(f"\n  {'Driver':<25} DNFs   Races  Finish Rate%  Nationality")
print(f"  {'-'*60}")
for _, row in dnf_drivers.iterrows():
    print(f"  {row['entity_name']:<25} {row['dnfs']:>4.0f}  {row['races']:>5.0f}  {row['finish_rate']:>8.1f}%     {row['nat']}")

subheader("KEY INSIGHTS")
print(f"  * {dnf_drivers.iloc[0]['entity_name']} has most DNFs: {dnf_drivers.iloc[0]['dnfs']:.0f} in {dnf_drivers.iloc[0]['races']:.0f} races")
print(f"  * DNF rate: {100 - dnf_drivers.iloc[0]['finish_rate']:.1f}%")
worst_finish = dnf_drivers.loc[dnf_drivers['finish_rate'].idxmin()]
print(f"  * Worst finish rate: {worst_finish['entity_name']} at {worst_finish['finish_rate']:.1f}%")


header("6. COMEBACK KINGS — GRID TO RACE POSITION GAINERS")
print(f"\n  {'Driver':<25} Avg Gained  Best Single Race  Comeback Races")
print(f"  {'-'*65}")
for _, row in comeback.iterrows():
    print(f"  {row['entity_name']:<25} {row['avg_gained']:>+7.2f}     {row['best_comeback']:>+8.0f}           {row['comeback_races']:>5.0f}")

subheader("KEY INSIGHTS")
print(f"  * {comeback.iloc[0]['entity_name']} gains avg {comeback.iloc[0]['avg_gained']:.2f} positions per race")
print(f"  * Best single race comeback: {comeback['best_comeback'].max():.0f} positions")


header("7. QUALIFYING — POLE POSITIONS")
print(f"\n  {'Driver':<25} Poles  Pole%   Front Row  Q3 Apps  Nationality")
print(f"  {'-'*65}")
for _, row in poles.iterrows():
    print(f"  {row['entity_name']:<25} {row['poles']:>4.0f}  {row['pole_pct']:>5.1f}%  {row['front_row']:>6.0f}     {row['q3']:>5.0f}    {row['nat']}")

subheader("KEY INSIGHTS")
print(f"  * {poles.iloc[0]['entity_name']} holds most poles: {poles.iloc[0]['poles']:.0f} ({poles.iloc[0]['pole_pct']:.1f}% of races)")
top3_poles = poles.head(3)['poles'].sum()
print(f"  * Top 3 combined poles: {top3_poles:.0f}")


header("8. POLE TO WIN CONVERSION")
print(f"\n  {'Driver':<25} Poles  Converted  Conversion%")
print(f"  {'-'*50}")
for _, row in pole_conversion.iterrows():
    print(f"  {row['entity_name']:<25} {row['total_poles']:>4.0f}  {row['converted']:>6.0f}     {row['conv_pct']:>6.1f}%")

subheader("KEY INSIGHTS")
best_conv = pole_conversion.loc[pole_conversion['conv_pct'].idxmax()]
print(f"  * Best conversion: {best_conv['entity_name']} — {best_conv['conv_pct']:.1f}%")
print(f"  * Most converted wins from pole: {pole_conversion.iloc[0]['entity_name']} ({pole_conversion.iloc[0]['converted']:.0f})")


header("9. CONSTRUCTORS — ALL TIME")
print(f"\n  {'Constructor':<25} Points    Wins  Reliability%  Avg Pts/Race  Nationality")
print(f"  {'-'*75}")
for _, row in constructors_all.iterrows():
    print(f"  {row['entity_name']:<25} {row['points']:>7.1f}  {row['wins']:>4.0f}  {row['reliability']:>8.1f}%    {row['avg_pts']:>8.3f}     {row['nat']}")

subheader("KEY INSIGHTS")
print(f"  * {constructors_all.iloc[0]['entity_name']} leads with {constructors_all.iloc[0]['points']:.0f} points")
best_rel = constructor_rel.iloc[0]
print(f"  * Most reliable constructor: {best_rel['entity_name']} at {best_rel['rel_pct']:.1f}%")
best_avg = constructors_all.loc[constructors_all['avg_pts'].idxmax()]
print(f"  * Best avg points/race: {best_avg['entity_name']} — {best_avg['avg_pts']:.3f}")


header("10. CONSTRUCTOR NATIONALITY DISTRIBUTION")
print(f"\n  {'Nationality':<15} Constructors  Total Points    Wins   Podiums")
print(f"  {'-'*60}")
for _, row in const_nat.iterrows():
    print(f"  {row['entity_name']:<15} {row['constructors']:>6.0f}       {row['points']:>10.1f}  {row['wins']:>6.0f}  {row['podiums']:>6.0f}")


header("11. CIRCUITS — MOST RACES HOSTED")
print(f"\n  {'Circuit':<30} Hosted  Active Seasons  Country")
print(f"  {'-'*65}")
for _, row in circuit_races.iterrows():
    print(f"  {row['entity_name']:<30} {row['hosted']:>4.0f}   {row['active']:>6.0f}          {row['country']}")

subheader("KEY INSIGHTS")
print(f"  * {circuit_races.iloc[0]['entity_name']} hosted most races: {circuit_races.iloc[0]['hosted']:.0f}")
print(f"  * {len(circuit_races)} circuits in dataset across {circuit_races['country'].nunique()} countries")


header("12. MOST DIFFICULT CIRCUITS — HIGHEST DNF RATE")
print(f"\n  {'Circuit':<30} DNF Rate%  Total DNFs  Races Hosted  Country")
print(f"  {'-'*70}")
for _, row in difficult_circuits.iterrows():
    print(f"  {row['entity_name']:<30} {row['dnf_rate']:>6.1f}%    {row['dnfs']:>6.0f}      {row['hosted']:>5.0f}        {row['country']}")

subheader("KEY INSIGHTS")
print(f"  * {difficult_circuits.iloc[0]['entity_name']} is most brutal — {difficult_circuits.iloc[0]['dnf_rate']:.1f}% DNF rate")
print(f"  * Top 3 dangerous circuits avg DNF: {difficult_circuits.head(3)['dnf_rate'].mean():.1f}%")


header("13. RETIRED CIRCUITS (BEFORE 2000)")
print(f"\n  {'Circuit':<30} Active Period     Races  Country")
print(f"  {'-'*65}")
for _, row in retired_circuits.iterrows():
    print(f"  {row['entity_name']:<30} {int(row['first_year'])}-{int(row['last_year'])}           {row['hosted']:>4.0f}   {row['country']}")


header("14. SEASON TRENDS SUMMARY")
print(f"\n  {'Season':<8} Races  Drivers  Points Awarded  DNF Rate%")
print(f"  {'-'*55}")
for _, row in season_growth.iterrows():
    print(f"  {int(row['season']):<8} {row['total_races']:>4.0f}   {row['drivers']:>4.0f}    {row['points']:>10.1f}     {row['dnf_rate']:>6.1f}%")

subheader("KEY INSIGHTS")
print(f"  * First season: {int(season_growth['season'].min())} — Last season: {int(season_growth['season'].max())}")
print(f"  * Max races in a season: {season_growth['total_races'].max():.0f} (Season {int(season_growth.loc[season_growth['total_races'].idxmax(),'season'])})")
print(f"  * Highest DNF rate season: {int(season_growth.loc[season_growth['dnf_rate'].idxmax(),'season'])} at {season_growth['dnf_rate'].max():.1f}%")
print(f"  * Most drivers in a season: {season_growth['drivers'].max():.0f} (Season {int(season_growth.loc[season_growth['drivers'].idxmax(),'season'])})")
print(f"  * Total points ever awarded: {season_growth['points'].sum():.0f}")


header("15. AVG POINTS PER RACE PER SEASON")
print(f"\n  {'Season':<8} Avg Pts/Race  Races  Total Points")
print(f"  {'-'*45}")
for _, row in season_avg_pts.iterrows():
    print(f"  {int(row['season']):<8} {row['avg_pts']:>8.2f}      {row['races']:>4.0f}   {row['total_pts']:>8.1f}")

subheader("KEY INSIGHTS")
max_avg = season_avg_pts.loc[season_avg_pts['avg_pts'].idxmax()]
min_avg = season_avg_pts.loc[season_avg_pts['avg_pts'].idxmin()]
print(f"  * Highest avg pts/race: Season {int(max_avg['season'])} — {max_avg['avg_pts']:.2f} pts")
print(f"  * Lowest avg pts/race:  Season {int(min_avg['season'])} — {min_avg['avg_pts']:.2f} pts")
print(f"  * Overall avg across all seasons: {season_avg_pts['avg_pts'].mean():.2f} pts/race")


header("16. NATIONALITY DOMINANCE — DRIVERS")
print(f"\n  {'Nationality':<20} Drivers  Total Points    Wins   Podiums")
print(f"  {'-'*60}")
for _, row in nat_dom.iterrows():
    print(f"  {row['entity_name']:<20} {row['drivers']:>5.0f}   {row['points']:>10.1f}  {row['wins']:>6.0f}  {row['podiums']:>6.0f}")

subheader("KEY INSIGHTS")
print(f"  * {nat_dom.iloc[0]['entity_name']} drivers dominate with {nat_dom.iloc[0]['points']:.0f} total points")
print(f"  * {nat_dom.iloc[0]['entity_name']} wins: {nat_dom.iloc[0]['wins']:.0f} — Podiums: {nat_dom.iloc[0]['podiums']:.0f}")


header("17. DATA QUALITY VALIDATION")
print(f"\n  {'Table':<30} Raw     Clean   Duplicates  Null Keys  Status")
print(f"  {'-'*70}")
for _, row in validation.iterrows():
    status = 'PASS' if row['null_key_fields']==0 else 'REVIEW'
    flag = '✓' if status=='PASS' else '!'
    print(f"  {row['table_name']:<30} {row['raw_count']:>5}   {row['clean_count']:>5}   {row['duplicates_removed']:>6}      {row['null_key_fields']:>5}      [{flag}] {status}")

subheader("SUMMARY")
total_raw = validation['raw_count'].sum()
total_clean = validation['clean_count'].sum()
total_dup = validation['duplicates_removed'].sum()
print(f"  * Total raw rows across all tables:   {total_raw:,}")
print(f"  * Total clean rows across all tables: {total_clean:,}")
print(f"  * Total duplicates removed:           {total_dup:,}")
all_pass = (validation['null_key_fields'] == 0).all()
print(f"  * Overall data quality: {'ALL PASS ✓' if all_pass else 'SOME TABLES NEED REVIEW'}")

print(f"\n{SEP}")
print(f"  REPORT COMPLETE — 18 graphs saved in ./graphs/ folder")
print(SEP)