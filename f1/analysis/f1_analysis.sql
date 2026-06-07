USE f1_analysis;
SET SQL_SAFE_UPDATES = 0;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS master_insights;
DROP TABLE IF EXISTS validation_checks;
DROP TABLE IF EXISTS season_analysis;
DROP TABLE IF EXISTS circuit_analysis;
DROP TABLE IF EXISTS constructor_analysis;
DROP TABLE IF EXISTS driver_analysis;
DROP TABLE IF EXISTS race_analysis;
DROP TABLE IF EXISTS clean_qualifying;
DROP TABLE IF EXISTS clean_results;
DROP TABLE IF EXISTS clean_races;
DROP TABLE IF EXISTS clean_drivers;
DROP TABLE IF EXISTS clean_constructors;
DROP TABLE IF EXISTS clean_circuits;
DROP TABLE IF EXISTS raw_circuits;
DROP TABLE IF EXISTS raw_constructors;
DROP TABLE IF EXISTS raw_drivers;
DROP TABLE IF EXISTS raw_races;
DROP TABLE IF EXISTS raw_results;
DROP TABLE IF EXISTS qualifying_analysis;
DROP TABLE IF EXISTS podium_analysis;
DROP TABLE IF EXISTS fastest_drivers;
DROP TABLE IF EXISTS driver_consistency;
DROP TABLE IF EXISTS constructor_race_wins;
DROP TABLE IF EXISTS race_competition;
DROP TABLE IF EXISTS qualifying_vs_race;
DROP TABLE IF EXISTS top_10_drivers;
DROP TABLE IF EXISTS driver_win_ratio;
DROP TABLE IF EXISTS constructor_dominance;
DROP TABLE IF EXISTS circuit_difficulty;
DROP TABLE IF EXISTS driver_improvement;
DROP TABLE IF EXISTS race_points_distribution;
DROP TABLE IF EXISTS driver_grid_vs_finish;
DROP TABLE IF EXISTS season_driver_points;
DROP TABLE IF EXISTS season_constructor_points;
DROP TABLE IF EXISTS season_monthly_races;
DROP TABLE IF EXISTS race_overview;
DROP TABLE IF EXISTS driver_performance;
DROP TABLE IF EXISTS constructor_performance;

CREATE TABLE clean_circuits AS
SELECT DISTINCT circuit_id, TRIM(name) AS circuit_name,
    CAST(lat AS DECIMAL(10,6)) AS latitude, CAST(`long` AS DECIMAL(10,6)) AS longitude,
    TRIM(locality) AS locality, TRIM(country) AS country
FROM circuits WHERE circuit_id IS NOT NULL AND name IS NOT NULL;

CREATE TABLE clean_constructors AS
SELECT DISTINCT constructor_id, TRIM(name) AS constructor_name, TRIM(nationality) AS nationality
FROM constructors WHERE constructor_id IS NOT NULL AND name IS NOT NULL;

CREATE TABLE clean_drivers AS
SELECT DISTINCT driver_id, TRIM(givenName) AS first_name, TRIM(familyName) AS last_name,
    CONCAT(TRIM(givenName),' ',TRIM(familyName)) AS full_name, TRIM(nationality) AS nationality,
    CASE WHEN dob REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' THEN STR_TO_DATE(dob,'%Y-%m-%d') ELSE NULL END AS date_of_birth
FROM drivers WHERE driver_id IS NOT NULL AND givenName IS NOT NULL;

CREATE TABLE clean_races AS
SELECT DISTINCT race_id, CAST(season AS UNSIGNED) AS season, CAST(round AS UNSIGNED) AS round,
    TRIM(race_name) AS race_name,
    CASE WHEN date REGEXP '^[0-9]{4}-[0-9]{2}-[0-9]{2}$' THEN STR_TO_DATE(date,'%Y-%m-%d') ELSE NULL END AS race_date,
    TRIM(time) AS race_time, circuit_id
FROM races WHERE race_id IS NOT NULL;

CREATE TABLE clean_results AS
SELECT DISTINCT race_id, driver_id, constructor_id,
    COALESCE(CAST(grid AS UNSIGNED),0) AS grid_position,
    NULLIF(TRIM(position),'') AS finish_position,
    COALESCE(CAST(position_order AS UNSIGNED),0) AS position_order,
    COALESCE(CAST(points AS DECIMAL(6,2)),0.00) AS points,
    COALESCE(CAST(laps AS UNSIGNED),0) AS laps_completed,
    TRIM(status) AS race_status
FROM results WHERE race_id IS NOT NULL AND driver_id IS NOT NULL;

CREATE TABLE clean_qualifying AS
SELECT DISTINCT race_id, driver_id, constructor_id,
    COALESCE(CAST(position AS UNSIGNED),0) AS qualifying_position,
    NULLIF(TRIM(q1),'') AS q1_time, NULLIF(TRIM(q2),'') AS q2_time, NULLIF(TRIM(q3),'') AS q3_time
FROM qualifying WHERE race_id IS NOT NULL AND driver_id IS NOT NULL;

CREATE TABLE race_analysis AS
SELECT r.race_id, r.season, r.round, r.race_name, c.circuit_name, c.country, c.locality, r.race_date,
    COUNT(DISTINCT res.driver_id) AS total_drivers,
    COUNT(DISTINCT res.constructor_id) AS total_constructors,
    COALESCE(SUM(res.points),0) AS total_points_awarded,
    ROUND(AVG(res.position_order),2) AS avg_finish_position,
    MAX(res.points) AS highest_points_in_race,
    SUM(CASE WHEN res.race_status='Finished' THEN 1 ELSE 0 END) AS drivers_finished,
    SUM(CASE WHEN res.race_status!='Finished' THEN 1 ELSE 0 END) AS drivers_dnf,
    ROUND(SUM(CASE WHEN res.race_status='Finished' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS finish_rate_pct,
    MONTH(r.race_date) AS race_month
FROM clean_races r
JOIN clean_circuits c ON r.circuit_id=c.circuit_id
JOIN clean_results res ON r.race_id=res.race_id
GROUP BY r.race_id,r.season,r.round,r.race_name,c.circuit_name,c.country,c.locality,r.race_date;

CREATE TABLE driver_analysis AS
SELECT d.driver_id, d.full_name AS driver_name, d.nationality, d.date_of_birth,
    TIMESTAMPDIFF(YEAR,d.date_of_birth,CURDATE()) AS current_age,
    COUNT(DISTINCT res.race_id) AS races_participated,
    COALESCE(SUM(res.points),0) AS total_points,
    ROUND(SUM(res.points)/COUNT(DISTINCT res.race_id),3) AS avg_points_per_race,
    ROUND(AVG(res.grid_position),2) AS avg_grid_position,
    ROUND(AVG(res.position_order),2) AS avg_finish_position,
    ROUND(AVG(res.grid_position)-AVG(res.position_order),2) AS avg_positions_gained,
    SUM(CASE WHEN res.position_order=1 THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN res.position_order=2 THEN 1 ELSE 0 END) AS second_place,
    SUM(CASE WHEN res.position_order=3 THEN 1 ELSE 0 END) AS third_place,
    SUM(CASE WHEN res.position_order<=3 THEN 1 ELSE 0 END) AS podiums,
    SUM(CASE WHEN res.position_order<=5 THEN 1 ELSE 0 END) AS top5_finishes,
    SUM(CASE WHEN res.position_order<=10 THEN 1 ELSE 0 END) AS top10_finishes,
    ROUND(SUM(CASE WHEN res.position_order=1 THEN 1 ELSE 0 END)*100.0/COUNT(*),3) AS win_ratio_pct,
    ROUND(SUM(CASE WHEN res.position_order<=3 THEN 1 ELSE 0 END)*100.0/COUNT(*),3) AS podium_ratio_pct,
    MIN(res.position_order) AS best_finish, MAX(res.position_order) AS worst_finish,
    SUM(res.laps_completed) AS total_laps_completed,
    SUM(CASE WHEN res.race_status!='Finished' THEN 1 ELSE 0 END) AS dnf_count,
    ROUND(SUM(CASE WHEN res.race_status='Finished' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS finish_rate_pct,
    COALESCE(q.qualifying_sessions,0) AS qualifying_sessions,
    COALESCE(q.avg_qualifying_position,0) AS avg_qualifying_position,
    COALESCE(q.pole_positions,0) AS pole_positions,
    COALESCE(q.pole_ratio_pct,0) AS pole_ratio_pct,
    COALESCE(q.front_row_starts,0) AS front_row_starts,
    COALESCE(q.top10_qualifies,0) AS top10_qualifies,
    COALESCE(q.q3_appearances,0) AS q3_appearances,
    COALESCE(q.races_improved_from_grid,0) AS races_improved_from_grid,
    COALESCE(q.races_lost_from_grid,0) AS races_lost_from_grid,
    COALESCE(q.avg_positions_gained_from_grid,0) AS avg_positions_gained_from_grid,
    COALESCE(q.best_qualifying,0) AS best_qualifying,
    COALESCE(q.worst_qualifying,0) AS worst_qualifying
FROM clean_drivers d
JOIN clean_results res ON d.driver_id=res.driver_id
LEFT JOIN (
    SELECT q.driver_id,
        COUNT(q.race_id) AS qualifying_sessions,
        ROUND(AVG(q.qualifying_position),2) AS avg_qualifying_position,
        ROUND(AVG(q.qualifying_position)-AVG(r2.position_order),2) AS avg_positions_gained_from_grid,
        SUM(CASE WHEN q.qualifying_position=1 THEN 1 ELSE 0 END) AS pole_positions,
        ROUND(SUM(CASE WHEN q.qualifying_position=1 THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS pole_ratio_pct,
        SUM(CASE WHEN q.qualifying_position<=3 THEN 1 ELSE 0 END) AS front_row_starts,
        SUM(CASE WHEN q.qualifying_position<=10 THEN 1 ELSE 0 END) AS top10_qualifies,
        SUM(CASE WHEN q.q3_time IS NOT NULL THEN 1 ELSE 0 END) AS q3_appearances,
        SUM(CASE WHEN r2.position_order<q.qualifying_position THEN 1 ELSE 0 END) AS races_improved_from_grid,
        SUM(CASE WHEN r2.position_order>q.qualifying_position THEN 1 ELSE 0 END) AS races_lost_from_grid,
        MIN(q.qualifying_position) AS best_qualifying, MAX(q.qualifying_position) AS worst_qualifying
    FROM clean_qualifying q
    JOIN clean_results r2 ON q.race_id=r2.race_id AND q.driver_id=r2.driver_id
    GROUP BY q.driver_id
) q ON d.driver_id=q.driver_id
GROUP BY d.driver_id,d.full_name,d.nationality,d.date_of_birth,
    q.qualifying_sessions,q.avg_qualifying_position,q.pole_positions,q.pole_ratio_pct,
    q.front_row_starts,q.top10_qualifies,q.q3_appearances,q.races_improved_from_grid,
    q.races_lost_from_grid,q.avg_positions_gained_from_grid,q.best_qualifying,q.worst_qualifying;

CREATE TABLE constructor_analysis AS
SELECT c.constructor_id, c.constructor_name, c.nationality,
    COUNT(res.race_id) AS total_race_entries,
    COUNT(DISTINCT res.race_id) AS unique_races,
    COUNT(DISTINCT res.driver_id) AS total_drivers_used,
    COALESCE(SUM(res.points),0) AS total_points,
    ROUND(SUM(res.points)/COUNT(DISTINCT res.race_id),3) AS avg_points_per_race,
    ROUND(AVG(res.position_order),2) AS avg_finish_position,
    SUM(CASE WHEN res.position_order=1 THEN 1 ELSE 0 END) AS wins,
    SUM(CASE WHEN res.position_order<=3 THEN 1 ELSE 0 END) AS podiums,
    SUM(CASE WHEN res.position_order<=10 THEN 1 ELSE 0 END) AS top10_finishes,
    ROUND(SUM(CASE WHEN res.position_order=1 THEN 1 ELSE 0 END)*100.0/COUNT(DISTINCT res.race_id),3) AS win_ratio_pct,
    MAX(res.points) AS max_points_single_race,
    SUM(CASE WHEN res.race_status!='Finished' THEN 1 ELSE 0 END) AS total_dnfs,
    ROUND(SUM(CASE WHEN res.race_status='Finished' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS reliability_pct
FROM clean_constructors c
JOIN clean_results res ON c.constructor_id=res.constructor_id
GROUP BY c.constructor_id,c.constructor_name,c.nationality;

CREATE TABLE circuit_analysis AS
SELECT ci.circuit_id, ci.circuit_name, ci.country, ci.locality, ci.latitude, ci.longitude,
    COUNT(DISTINCT r.race_id) AS total_races_hosted,
    MIN(r.season) AS first_race_season, MAX(r.season) AS last_race_season,
    MAX(r.season)-MIN(r.season)+1 AS years_on_calendar,
    COUNT(DISTINCT r.season) AS active_seasons,
    ROUND(AVG(res.position_order),2) AS avg_finish_position,
    COALESCE(SUM(res.points),0) AS total_points_awarded,
    SUM(CASE WHEN res.race_status!='Finished' THEN 1 ELSE 0 END) AS total_dnfs,
    ROUND(SUM(CASE WHEN res.race_status!='Finished' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS avg_dnf_rate_pct,
    COUNT(DISTINCT res.driver_id) AS unique_drivers,
    COUNT(DISTINCT res.constructor_id) AS unique_constructors
FROM clean_circuits ci
JOIN clean_races r ON ci.circuit_id=r.circuit_id
JOIN clean_results res ON r.race_id=res.race_id
GROUP BY ci.circuit_id,ci.circuit_name,ci.country,ci.locality,ci.latitude,ci.longitude;

CREATE TABLE season_analysis AS
SELECT r.season,
    COUNT(DISTINCT r.race_id) AS total_races,
    COUNT(DISTINCT res.driver_id) AS unique_drivers,
    COUNT(DISTINCT res.constructor_id) AS unique_constructors,
    COALESCE(SUM(res.points),0) AS total_points_awarded,
    ROUND(AVG(res.points),3) AS avg_points_per_entry,
    SUM(CASE WHEN res.race_status!='Finished' THEN 1 ELSE 0 END) AS total_dnfs,
    ROUND(SUM(CASE WHEN res.race_status!='Finished' THEN 1 ELSE 0 END)*100.0/COUNT(*),2) AS dnf_rate_pct,
    COUNT(DISTINCT ci.country) AS countries_visited,
    MIN(r.race_date) AS season_start_date, MAX(r.race_date) AS season_end_date
FROM clean_races r
JOIN clean_results res ON r.race_id=res.race_id
JOIN clean_circuits ci ON r.circuit_id=ci.circuit_id
GROUP BY r.season;

CREATE TABLE validation_checks AS
SELECT 'circuits' AS table_name,
    (SELECT COUNT(*) FROM circuits) AS raw_count,
    (SELECT COUNT(*) FROM clean_circuits) AS clean_count,
    (SELECT COUNT(*) FROM circuits)-(SELECT COUNT(*) FROM clean_circuits) AS duplicates_removed,
    (SELECT COUNT(*) FROM clean_circuits WHERE circuit_name IS NULL OR country IS NULL) AS null_key_fields
UNION ALL SELECT 'constructors',
    (SELECT COUNT(*) FROM constructors),(SELECT COUNT(*) FROM clean_constructors),
    (SELECT COUNT(*) FROM constructors)-(SELECT COUNT(*) FROM clean_constructors),
    (SELECT COUNT(*) FROM clean_constructors WHERE constructor_name IS NULL)
UNION ALL SELECT 'drivers',
    (SELECT COUNT(*) FROM drivers),(SELECT COUNT(*) FROM clean_drivers),
    (SELECT COUNT(*) FROM drivers)-(SELECT COUNT(*) FROM clean_drivers),
    (SELECT COUNT(*) FROM clean_drivers WHERE full_name IS NULL OR nationality IS NULL)
UNION ALL SELECT 'races',
    (SELECT COUNT(*) FROM races),(SELECT COUNT(*) FROM clean_races),
    (SELECT COUNT(*) FROM races)-(SELECT COUNT(*) FROM clean_races),
    (SELECT COUNT(*) FROM clean_races WHERE race_date IS NULL)
UNION ALL SELECT 'results',
    (SELECT COUNT(*) FROM results),(SELECT COUNT(*) FROM clean_results),
    (SELECT COUNT(*) FROM results)-(SELECT COUNT(*) FROM clean_results),
    (SELECT COUNT(*) FROM clean_results WHERE driver_id IS NULL OR race_id IS NULL)
UNION ALL SELECT 'qualifying',
    (SELECT COUNT(*) FROM qualifying),(SELECT COUNT(*) FROM clean_qualifying),
    (SELECT COUNT(*) FROM qualifying)-(SELECT COUNT(*) FROM clean_qualifying),
    (SELECT COUNT(*) FROM clean_qualifying WHERE qualifying_position=0)
UNION ALL SELECT 'driver_standings',
    (SELECT COUNT(*) FROM driver_standings),(SELECT COUNT(*) FROM driver_standings),0,
    (SELECT COUNT(*) FROM driver_standings WHERE driver_id IS NULL OR season IS NULL)
UNION ALL SELECT 'constructor_standings',
    (SELECT COUNT(*) FROM constructor_standings),(SELECT COUNT(*) FROM constructor_standings),0,
    (SELECT COUNT(*) FROM constructor_standings WHERE constructor_id IS NULL OR season IS NULL)
UNION ALL SELECT 'f1_2025_last_race_results',
    (SELECT COUNT(*) FROM f1_2025_last_race_results),(SELECT COUNT(*) FROM f1_2025_last_race_results),0,0;

CREATE TABLE master_insights (
    insight_category  VARCHAR(50),
    insight_name      VARCHAR(100),
    entity_name       VARCHAR(200),
    season            INT,
    rank_no           INT,
    metric1_label     VARCHAR(60),
    metric1_value     DECIMAL(12,3),
    metric2_label     VARCHAR(60),
    metric2_value     DECIMAL(12,3),
    metric3_label     VARCHAR(60),
    metric3_value     DECIMAL(12,3),
    metric4_label     VARCHAR(60),
    metric4_value     DECIMAL(12,3),
    extra_info        VARCHAR(200)
);

INSERT INTO master_insights
SELECT 'Driver','Top Drivers All Time by Points',driver_name,NULL,
    RANK() OVER (ORDER BY total_points DESC),
    'races_participated',races_participated,
    'total_points',total_points,
    'wins',wins,
    'podiums',podiums,
    nationality
FROM driver_analysis ORDER BY total_points DESC LIMIT 10;

INSERT INTO master_insights
SELECT 'Driver','Best Driver Per Season',d.full_name,r.season,
    RANK() OVER (PARTITION BY r.season ORDER BY SUM(res.points) DESC),
    'season_points',SUM(res.points),
    'season_wins',SUM(CASE WHEN res.position_order=1 THEN 1 ELSE 0 END),
    'season_podiums',SUM(CASE WHEN res.position_order<=3 THEN 1 ELSE 0 END),
    'races_in_season',COUNT(res.race_id),
    d.nationality
FROM clean_results res
JOIN clean_races r ON res.race_id=r.race_id
JOIN clean_drivers d ON res.driver_id=d.driver_id
GROUP BY r.season,res.driver_id,d.full_name,d.nationality
HAVING SUM(res.points)=(
    SELECT MAX(sp.total) FROM (
        SELECT r2.season,res2.driver_id,SUM(res2.points) AS total
        FROM clean_results res2 JOIN clean_races r2 ON res2.race_id=r2.race_id
        GROUP BY r2.season,res2.driver_id
    ) sp WHERE sp.season=r.season
);

INSERT INTO master_insights
SELECT 'Driver','Top Win Ratio min50 Races',driver_name,NULL,
    RANK() OVER (ORDER BY win_ratio_pct DESC),
    'win_ratio_pct',win_ratio_pct,
    'wins',wins,
    'races_participated',races_participated,
    'podium_ratio_pct',podium_ratio_pct,
    nationality
FROM driver_analysis WHERE races_participated>=50 ORDER BY win_ratio_pct DESC LIMIT 10;

INSERT INTO master_insights
SELECT 'Driver','Most Consistent Drivers',driver_name,NULL,
    RANK() OVER (ORDER BY avg_finish_position ASC),
    'avg_finish_position',avg_finish_position,
    'best_finish',best_finish,
    'worst_finish',worst_finish,
    'finish_rate_pct',finish_rate_pct,
    nationality
FROM driver_analysis WHERE races_participated>=20 ORDER BY avg_finish_position ASC LIMIT 15;

INSERT INTO master_insights
SELECT 'Driver','Drivers With Most DNFs',driver_name,NULL,
    RANK() OVER (ORDER BY dnf_count DESC),
    'dnf_count',dnf_count,
    'finish_rate_pct',finish_rate_pct,
    'races_participated',races_participated,
    'total_points',total_points,
    nationality
FROM driver_analysis ORDER BY dnf_count DESC LIMIT 15;

INSERT INTO master_insights
SELECT 'Driver','Veteran Drivers 100+ Races',driver_name,NULL,
    RANK() OVER (ORDER BY races_participated DESC),
    'races_participated',races_participated,
    'total_points',total_points,
    'wins',wins,
    'avg_points_per_race',avg_points_per_race,
    nationality
FROM driver_analysis WHERE races_participated>=100 ORDER BY races_participated DESC;

INSERT INTO master_insights
SELECT 'Driver','Driver Comeback Performance',da.driver_name,NULL,
    RANK() OVER (ORDER BY ROUND(AVG(res.grid_position-res.position_order),2) DESC),
    'avg_positions_gained',ROUND(AVG(res.grid_position-res.position_order),2),
    'comeback_races',SUM(CASE WHEN res.position_order<res.grid_position THEN 1 ELSE 0 END),
    'best_single_race_comeback',MAX(res.grid_position-res.position_order),
    'races_participated',da.races_participated,
    da.nationality
FROM driver_analysis da
JOIN clean_results res ON da.driver_id=res.driver_id
GROUP BY da.driver_id,da.driver_name,da.nationality,da.races_participated
ORDER BY ROUND(AVG(res.grid_position-res.position_order),2) DESC LIMIT 15;

INSERT INTO master_insights
SELECT 'Driver','Most Points In Single Race',d.full_name,r.season,
    RANK() OVER (ORDER BY res.points DESC),
    'points',res.points,
    'finish_position',res.position_order,
    'grid_position',res.grid_position,
    NULL,NULL,
    r.race_name
FROM clean_results res
JOIN clean_drivers d ON res.driver_id=d.driver_id
JOIN clean_races r ON res.race_id=r.race_id
ORDER BY res.points DESC LIMIT 10;

INSERT INTO master_insights
SELECT 'Driver','Nationality Dominance',d.nationality,NULL,
    RANK() OVER (ORDER BY SUM(res.points) DESC),
    'total_drivers',COUNT(DISTINCT d.driver_id),
    'total_points',SUM(res.points),
    'total_wins',SUM(CASE WHEN res.position_order=1 THEN 1 ELSE 0 END),
    'total_podiums',SUM(CASE WHEN res.position_order<=3 THEN 1 ELSE 0 END),
    NULL
FROM clean_drivers d
JOIN clean_results res ON d.driver_id=res.driver_id
GROUP BY d.nationality ORDER BY SUM(res.points) DESC LIMIT 15;

INSERT INTO master_insights
SELECT 'Qualifying','Most Pole Positions All Time',driver_name,NULL,
    RANK() OVER (ORDER BY pole_positions DESC),
    'pole_positions',pole_positions,
    'pole_ratio_pct',pole_ratio_pct,
    'front_row_starts',front_row_starts,
    'q3_appearances',q3_appearances,
    nationality
FROM driver_analysis ORDER BY pole_positions DESC LIMIT 10;

INSERT INTO master_insights
SELECT 'Qualifying','Best Grid to Race Improvers',driver_name,NULL,
    RANK() OVER (ORDER BY avg_positions_gained_from_grid DESC),
    'avg_positions_gained_from_grid',avg_positions_gained_from_grid,
    'races_improved_from_grid',races_improved_from_grid,
    'pole_positions',pole_positions,
    'qualifying_sessions',qualifying_sessions,
    nationality
FROM driver_analysis WHERE qualifying_sessions>=10
ORDER BY avg_positions_gained_from_grid DESC LIMIT 15;

INSERT INTO master_insights
SELECT 'Qualifying','Poles Converted to Wins',da.driver_name,NULL,
    RANK() OVER (ORDER BY SUM(CASE WHEN cq.qualifying_position=1 AND res.position_order=1 THEN 1 ELSE 0 END) DESC),
    'poles_converted_to_wins',SUM(CASE WHEN cq.qualifying_position=1 AND res.position_order=1 THEN 1 ELSE 0 END),
    'total_poles',da.pole_positions,
    'conversion_rate_pct',CASE WHEN da.pole_positions>0
        THEN ROUND(SUM(CASE WHEN cq.qualifying_position=1 AND res.position_order=1 THEN 1 ELSE 0 END)*100.0/da.pole_positions,2)
        ELSE 0 END,
    NULL,NULL,
    NULL
FROM driver_analysis da
JOIN clean_qualifying cq ON da.driver_id=cq.driver_id
JOIN clean_results res ON cq.race_id=res.race_id AND cq.driver_id=res.driver_id
GROUP BY da.driver_id,da.driver_name,da.pole_positions
ORDER BY SUM(CASE WHEN cq.qualifying_position=1 AND res.position_order=1 THEN 1 ELSE 0 END) DESC LIMIT 10;

INSERT INTO master_insights
SELECT 'Constructor','Constructor All Time Performance',constructor_name,NULL,
    RANK() OVER (ORDER BY total_points DESC),
    'total_points',total_points,
    'wins',wins,
    'reliability_pct',reliability_pct,
    'avg_points_per_race',avg_points_per_race,
    nationality
FROM constructor_analysis ORDER BY total_points DESC;

INSERT INTO master_insights
SELECT 'Constructor','Constructor Dominance By Season',c.constructor_name,r.season,
    RANK() OVER (PARTITION BY r.season ORDER BY SUM(res.points) DESC),
    'season_points',SUM(res.points),
    'season_wins',SUM(CASE WHEN res.position_order=1 THEN 1 ELSE 0 END),
    'season_point_share_pct',ROUND(SUM(res.points)*100.0/SUM(SUM(res.points)) OVER (PARTITION BY r.season),2),
    'season_podiums',SUM(CASE WHEN res.position_order<=3 THEN 1 ELSE 0 END),
    c.nationality
FROM clean_results res
JOIN clean_races r ON res.race_id=r.race_id
JOIN clean_constructors c ON res.constructor_id=c.constructor_id
GROUP BY r.season,res.constructor_id,c.constructor_name,c.nationality
ORDER BY r.season,SUM(res.points) DESC;

INSERT INTO master_insights
SELECT 'Constructor','Constructor Reliability Ranking',constructor_name,NULL,
    RANK() OVER (ORDER BY reliability_pct DESC),
    'reliability_pct',reliability_pct,
    'total_dnfs',total_dnfs,
    'total_points',total_points,
    'wins',wins,
    nationality
FROM constructor_analysis ORDER BY reliability_pct DESC LIMIT 15;

INSERT INTO master_insights
SELECT 'Constructor','Constructor Nationality Distribution',c.nationality,NULL,
    RANK() OVER (ORDER BY SUM(res.points) DESC),
    'constructors',COUNT(DISTINCT c.constructor_id),
    'total_points',SUM(res.points),
    'wins',SUM(CASE WHEN res.position_order=1 THEN 1 ELSE 0 END),
    'podiums',SUM(CASE WHEN res.position_order<=3 THEN 1 ELSE 0 END),
    NULL
FROM clean_constructors c
JOIN clean_results res ON c.constructor_id=res.constructor_id
GROUP BY c.nationality ORDER BY SUM(res.points) DESC;

INSERT INTO master_insights
SELECT 'Race','Most Competitive Races',race_name,season,
    RANK() OVER (ORDER BY total_drivers DESC),
    'total_drivers',total_drivers,
    'drivers_dnf',drivers_dnf,
    'finish_rate_pct',finish_rate_pct,
    'total_points_awarded',total_points_awarded,
    circuit_name
FROM race_analysis ORDER BY total_drivers DESC LIMIT 10;

INSERT INTO master_insights
SELECT 'Race','Highest Points Races',race_name,season,
    RANK() OVER (ORDER BY total_points_awarded DESC),
    'total_points_awarded',total_points_awarded,
    'total_drivers',total_drivers,
    'finish_rate_pct',finish_rate_pct,
    'highest_points_in_race',highest_points_in_race,
    circuit_name
FROM race_analysis ORDER BY total_points_awarded DESC LIMIT 10;

INSERT INTO master_insights
SELECT 'Circuit','Most Races Hosted',circuit_name,NULL,
    RANK() OVER (ORDER BY total_races_hosted DESC),
    'total_races_hosted',total_races_hosted,
    'active_seasons',active_seasons,
    'unique_drivers',unique_drivers,
    'unique_constructors',unique_constructors,
    country
FROM circuit_analysis ORDER BY total_races_hosted DESC LIMIT 15;

INSERT INTO master_insights
SELECT 'Circuit','Most Difficult Circuits High DNF Rate',circuit_name,NULL,
    RANK() OVER (ORDER BY avg_dnf_rate_pct DESC),
    'avg_dnf_rate_pct',avg_dnf_rate_pct,
    'total_dnfs',total_dnfs,
    'total_races_hosted',total_races_hosted,
    'unique_drivers',unique_drivers,
    country
FROM circuit_analysis ORDER BY avg_dnf_rate_pct DESC LIMIT 10;

INSERT INTO master_insights
SELECT 'Circuit','Retired Circuits Before 2000',circuit_name,NULL,
    RANK() OVER (ORDER BY last_race_season DESC),
    'last_race_season',last_race_season,
    'first_race_season',first_race_season,
    'total_races_hosted',total_races_hosted,
    NULL,NULL,
    country
FROM circuit_analysis WHERE last_race_season<2000 ORDER BY last_race_season DESC LIMIT 15;

INSERT INTO master_insights
SELECT 'Season','Season Growth Trend',CAST(season AS CHAR),season,
    RANK() OVER (ORDER BY season ASC),
    'total_races',total_races,
    'unique_drivers',unique_drivers,
    'total_points_awarded',total_points_awarded,
    'dnf_rate_pct',dnf_rate_pct,
    NULL
FROM season_analysis ORDER BY season;

INSERT INTO master_insights
SELECT 'Season','Season Highest DNF Rate',CAST(season AS CHAR),season,
    RANK() OVER (ORDER BY dnf_rate_pct DESC),
    'dnf_rate_pct',dnf_rate_pct,
    'total_dnfs',total_dnfs,
    'total_races',total_races,
    'unique_drivers',unique_drivers,
    NULL
FROM season_analysis ORDER BY dnf_rate_pct DESC LIMIT 10;

INSERT INTO master_insights
SELECT 'Season','Avg Points Per Race Per Season',CAST(r.season AS CHAR),r.season,
    RANK() OVER (ORDER BY r.season ASC),
    'avg_points_per_race',ROUND(SUM(res.points)/COUNT(DISTINCT r.race_id),2),
    'races_in_season',COUNT(DISTINCT r.race_id),
    'total_points',SUM(res.points),
    NULL,NULL,
    NULL
FROM clean_results res
JOIN clean_races r ON res.race_id=r.race_id
GROUP BY r.season ORDER BY r.season;

INSERT INTO master_insights
SELECT 'Validation','Data Quality Check',table_name,NULL,
    ROW_NUMBER() OVER (ORDER BY table_name),
    'raw_count',raw_count,
    'clean_count',clean_count,
    'duplicates_removed',duplicates_removed,
    'null_key_fields',null_key_fields,
    CASE WHEN null_key_fields=0 THEN 'PASS' ELSE 'REVIEW' END
FROM validation_checks;

DROP TABLE IF EXISTS circuits;
DROP TABLE IF EXISTS constructors;
DROP TABLE IF EXISTS drivers;
DROP TABLE IF EXISTS races;
DROP TABLE IF EXISTS results;
DROP TABLE IF EXISTS qualifying;
DROP TABLE IF EXISTS constructor_standings;
DROP TABLE IF EXISTS driver_standings;
DROP TABLE IF EXISTS f1_2025_last_race_results;

SHOW TABLES;

SELECT * FROM clean_circuits;
SELECT * FROM clean_constructors;
SELECT * FROM clean_drivers;
SELECT * FROM clean_races;
SELECT * FROM clean_results;
SELECT * FROM clean_qualifying;
SELECT * FROM race_analysis;
SELECT * FROM driver_analysis;
SELECT * FROM constructor_analysis;
SELECT * FROM circuit_analysis;
SELECT * FROM season_analysis;
SELECT * FROM validation_checks;
SELECT * FROM master_insights ORDER BY insight_category, insight_name, rank_no;
