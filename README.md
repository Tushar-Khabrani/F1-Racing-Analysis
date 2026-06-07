# 🏎️ F1 Racing Analysis (1950–2025)

![Python](https://img.shields.io/badge/Python-3.x-blue) ![MySQL](https://img.shields.io/badge/MySQL-8.0-orange) ![Pandas](https://img.shields.io/badge/Pandas-green) ![Matplotlib](https://img.shields.io/badge/Matplotlib-red) ![Seaborn](https://img.shields.io/badge/Seaborn-purple)

End-to-end Formula 1 racing data analysis spanning **1950–2025** using Python and MySQL — covering driver performance, constructor standings, circuit analysis, and championship progression across 1,149 races and 7,600+ records.

---

## 📦 Dataset Overview

| Dataset | Records |
|---------|---------|
| races.csv | 1,149 races |
| results.csv | 7,600+ entries |
| drivers.csv | All F1 drivers |
| constructors.csv | All F1 teams |
| qualifying.csv | Qualifying data |
| driver_standings.csv | Season standings |
| constructor_standings.csv | Constructor standings |
| circuits.csv | Circuit details |
| f1_2025_last_race_results.csv | Latest 2025 race |

**Year Range:** 1950 – 2025 | **Data Quality:** 47 duplicates resolved · all primary tables passed null-key checks

---

## 🏆 Key Stats

| Metric | Value |
|--------|-------|
| All-Time Points Leader | Lewis Hamilton (1,206 pts) |
| Most Race Wins | Michael Schumacher |
| Best Win Ratio (50+ races) | Schumacher 34.1% |
| Most Poles | Hamilton (29) |
| Best Pole-to-Win | Norris & Piastri (100%) |
| Top Constructor | Ferrari (3,404 pts) |
| Most Hosted Circuit | Monza (75 races) |
| Highest DNF Rate Circuit | Estoril & Okayama (92.3%) |

---

## 💡 Key Insights

- **Hamilton dominates** all-time points (1,206) — Vettel 2nd (812), Verstappen 3rd (733)
- **Win ratios (min 50 races):** Schumacher 34.1% · Prost 32.7% · Verstappen 27.3% · Hamilton 23.9% · Vettel 19.2%
- **Most consistent:** Hamilton avg finish 4.49 · Schumacher 6.05 · Verstappen 6.33
- **Most DNFs:** Hill (58) · Barrichello (52)
- **Pole-to-win conversion:** Norris & Piastri 100% · Räikkönen 80% · Verstappen 66.7%
- **Constructors:** Ferrari (3,404) · Mercedes (2,029) · McLaren (2,026) · Red Bull (1,926) · Williams (955)
- **Nationality dominance:** British constructors led (5,691 pts) · British drivers led (3,606 pts)
- **Circuit DNF rates:** Estoril & Okayama highest (92.3%) · Donington Park (92.0%)
- **Season evolution:** 1950s had 7–11 races/season · avg pts per race dropped from 16.29 (1950) to 12.91 (1958)

---

## 📈 Visualizations (17 Charts)

| Chart | Description |
|-------|-------------|
| `01_top_drivers_alltime` | All-time driver rankings by points, wins, podiums |
| `02_season_champions` | Season-by-season championship winners |
| `03_season_points_heatmap` | Points heatmap across seasons and drivers |
| `04_win_ratio_consistency` | Win ratio vs consistency scatter (min 50 races) |
| `05_dnf_comebacks` | Most DNFs and best grid position gainers |
| `06_qualifying_analysis` | Pole positions and pole-to-win conversion rates |
| `07_grid_improvers` | Drivers who gained most positions from grid to finish |
| `08_constructors_alltime` | Constructor all-time points, wins, reliability |
| `09_nationality_dominance` | Points and wins by driver/constructor nationality |
| `10_circuits_analysis` | Most hosted circuits and race counts |
| `11_retired_circuits` | Historic circuits no longer on the calendar |
| `12_season_trends` | Season-level trends — races, drivers, points |
| `13_avg_points_per_season` | Avg points per race across seasons |
| `14_season_dnf_rates` | DNF rate evolution by season |
| `15_data_quality` | Data validation summary — raw vs clean counts |
| `17_veteran_drivers` | Drivers with 100+ race starts |
| `18_constructor_season_trends` | Top 5 constructor points trends across seasons |

---

## 🗄️ SQL Analysis

- Cleaned and integrated 8 relational tables using advanced JOINs
- Resolved 47 duplicate rows via key-based validation
- Career stats per driver — points, wins, podiums, DNFs, avg finish
- Season champions via final-round standings filter
- Win ratio, consistency, comeback, and pole-to-win conversion analysis
- Constructor performance — reliability rate, avg points per race
- Circuit hosting history and DNF rate by venue
- Data validation table — raw vs clean count comparison

---

## 📁 Project Structure

    f1-racing-analysis/
    ├── analysis.py
    ├── compute_insights.py
    ├── data_summary.py
    ├── f1_analysis.sql
    ├── data/
    │   ├── results.csv
    │   ├── drivers.csv
    │   ├── constructors.csv
    │   ├── circuits.csv
    │   ├── races.csv
    │   ├── qualifying.csv
    │   ├── driver_standings.csv
    │   ├── constructor_standings.csv
    │   └── f1_2025_last_race_results.csv
    ├── graphs/
    │   └── (17 chart PNGs)
    └── README.md

---

## ▶️ How to Run

1. Clone: `git clone https://github.com/tushar-khabrani/f1-racing-analysis`
2. Import CSVs into MySQL
3. Run `f1_analysis.sql` in MySQL Workbench
4. Install: `pip install pandas matplotlib seaborn`
5. Run: `python analysis.py`

---

## 🤖 AI Integration
AI tools used for Python scripting, SQL optimization, and README drafting — all racing insights independently analyzed and validated.

---

## 👤 Author
**Tushar Khabrani** — [LinkedIn](https://www.linkedin.com/in/tusharkhabrani104) · [GitHub](https://github.com/tushar-khabrani)
