          **WMATA Real‑Time Bus Route Performance & Simulation Dashboard**

<p align="center">
<img src="assets/wmata_header.png" width="100%" alt="WMATA Dashboard Banner">
</p>

**Project Overview**
The WMATA Real‑Time Bus Route Performance & Simulation Dashboard is a modern, data‑driven platform designed to analyze, visualize, and simulate transit operations across Washington, DC’s busiest bus corridors.

It integrates:

Realistic synthetic transit data

Route‑level KPIs

Stop‑level analytics

Interactive map visualizations

A real‑time animated bus simulation

A clean, WMATA‑themed glass‑panel UI

This dashboard is built for:

Transit planners

Government analytics teams

Researchers

Students

Data scientists building portfolio‑ready projects

**Problem Statement**
Urban bus systems face persistent challenges:

Unpredictable delays

Irregular headways

Overcrowding at key stops

Limited real‑time visibility

Difficulty communicating performance insights

WMATA corridors such as S2/S4, 70/79, and X2 experience:

Traffic congestion

Bunching

Schedule drift

Peak‑hour overload

The gap:  
There is no unified, interactive dashboard that combines real‑time bus movement, route performance, stop‑level analytics, and system‑wide KPIs in one place.

This project fills that gap.

**Objectives**
✔ Build a WMATA‑style transit analytics dashboard
✔ Simulate real‑time bus movement along DC corridors
✔ Visualize route polylines, delays, loads, and performance
✔ Provide planners with actionable KPIs
✔ Deliver a clean, modern, glass‑panel UI
✔ Enable route‑by‑route animated playback
✔ Support future integration with GTFS‑RT feeds
** Methodology**
Data Generation
A custom generator produces realistic:

Route shapes

Stop locations

Trip schedules

Delays

Passenger loads

Vehicle positions (every 20 seconds)

**KPI Computation**
Metrics include:

Delay

On‑time performance (OTP)

Load factor

Peak crowding

Reliability score

Crowding score

Composite route score

Automated recommendations

## 📊 Understanding the KPIs

Below are the core metrics used in the WMATA Bus Route Performance Dashboard:

| Metric              | Meaning               | How Calculated              | Interpretation      |
| ------------------- | --------------------- | --------------------------- | ------------------- |
| **Avg Delay (min)** | Average lateness      | Mean(actual − scheduled)    | 1.5 min = very good |
| **OTP (%)**         | On‑Time Performance   | % of arrivals within ±5 min | 96.3% = excellent   |
| **Avg Load Factor** | Bus fullness          | load ÷ capacity             | 0.43 = 43% full     |
| **Avg Route Score** | Composite performance | Weighted KPI formula        | 0.5 = moderate      |

**Visualization Stack - Streamlit for UI**

Plotly for charts and Mapbox maps

Animated frames for real‑time simulation

Custom WMATA color palette

Glass‑panel UI with blurred header image

**Simulation Engine**
Smooth bus movement

Timestamp‑based animation

Route polylines

Auto‑play loop

** Application of the Project**

- Transit Planners
  Identify delay hotspots, crowding, and reliability issues.

- Government Agencies
  Support capital planning and service optimization.

- Researchers
  Study transit operations and real‑time analytics.

- Developers
  Extend to GTFS‑RT, ML predictions, or live dashboards.

- How to Use the Dashboard

1. Generate Data
   bash
   python src/generate_data.py
2. Run the Dashboard
   bash
   streamlit run src/dashboard_app.py
3. Explore the Tabs

- System Overview
  High‑level KPIs across all routes.

- Route Performance
  Delay, OTP, load factor, reliability, crowding, recommendations.

- Stop Analysis
  Stop‑level delay and passenger load patterns.

- Map View
  Clustered stop delays on a DC map.

- Real‑Time Simulation
  Animated buses moving along DC corridors.

- Lessons Learned
  ✔ Realistic transit simulation requires careful modeling
  ✔ Animation requires optimized frame generation
  ✔ KPI logic must match the dataset
  ✔ UI/UX dramatically improves clarity
  ✔ Streamlit + Plotly = powerful for real‑time dashboards
- Nxt Steps
  -TFS‑RT Integration
  Live WMATA vehicle positions + trip updates.

- Bus Bunching Detection
  Real‑time headway irregularity scoring.

- Delay Heatmaps
  Spatial visualization of delay intensity.

- Corridor Performance Index
  Combine S2/S4 + 70/79 + X2 into a unified score.

- Predictive Modeling
  Forecast delays, crowding, and travel times.

- Operator Performance Metrics
  Shift‑level reliability and adherence scoring.

-Final Notes
This project demonstrates:

Data engineering

Simulation modeling

Visualization engineering

UI/UX design

Transit analytics

It is portfolio‑ready, professional, and agency‑grade.
