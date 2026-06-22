# 🔧 Equipment Maintenance Intelligent Decision System

> **Knowledge Engineering Final Project — Master's Program**
> **Author: Omar**

*This project was created by Omar. Repository hosted by a classmate only to share a viewable link.*

### 🌐 Live interactive demo (no install, works in China): **https://fayazpainda.github.io/equipment-maintenance/**

An AI-powered Jupyter Notebook application that monitors industrial equipment sensor data in real time, scores risk levels, detects anomalies, visualizes trends, and generates plain-English maintenance recommendations — before failures happen.

> ✅ **Runs fully offline — no API key, no internet required.** The recommendation engine uses a built-in maintenance expert system by default, so the notebook works **anywhere in the world (including mainland China)** and during an offline presentation. Using **Claude (LLM)** is an optional upgrade (see Section 5).

---

## 🎯 Problem Statement

Unplanned industrial equipment failures cost manufacturers an average of **$260,000+ per hour** in downtime. Maintenance teams currently rely on fixed inspection schedules or react only after failures occur. This system shifts that to **predictive, data-driven decision-making**.

**Target users:** Maintenance engineers and plant managers  
**Decision type:** Predictive maintenance scheduling  
**Core question:** *Which machines need attention right now, why, and what exactly should be done?*

---

## 🚀 Quickstart

### 1. Install dependencies
```bash
pip install pandas numpy matplotlib scikit-learn ipywidgets
```
> `anthropic` is **optional** — only needed if you turn on the online Claude mode below. The notebook runs without it.

### 2. Launch Jupyter
```bash
jupyter notebook equipment_maintenance.ipynb
```
> ⚠️ Use **Jupyter Notebook or JupyterLab** — not VS Code. Widgets require a live kernel.
> Google Colab also works (free, supports notebooks). PythonAnywhere free is **not** suitable — it has no Jupyter/widget support.

### 3. Run all cells
`Kernel → Restart & Run All`, then interact with widgets in each section. **No API key needed** — the offline expert engine produces the maintenance recommendations.

### 4. (Optional) Enable Claude instead of the offline engine
In Section 1, set `USE_LLM_API = True` and provide a real key:
```python
ANTHROPIC_API_KEY = 'sk-ant-...'   # or: export ANTHROPIC_API_KEY=sk-ant-...
```
Then `pip install anthropic`. If the API is ever unreachable, the notebook automatically falls back to the offline engine, so the demo never breaks.

---

## 📁 Project Structure

```
equipment_maintenance/
├── equipment_maintenance.ipynb   ← Main notebook
├── README.md                     ← This file
└── data/                         ← Auto-created on first run
    ├── equipment_data.csv        ← Simulated sensor dataset
    ├── risk_trends.png           ← Risk trend charts
    ├── fleet_dashboard.png       ← Fleet overview
    └── anomaly_scatter.png       ← Anomaly scatter plot
```

---

## 🧩 System Architecture

```
INPUT       →  Sliders (live)  |  CSV Upload  |  Simulated Data
                    ↓
ANALYSIS    →  Rule-based Risk Scoring (0–100)
               IsolationForest Anomaly Detection
               Fleet Summary & Decision Engine
                    ↓
DISPLAY     →  Trend Charts | Fleet Dashboard | Heatmap | Alert Table
                    ↓
ADVISOR     →  Offline expert system (default) OR Claude API → 5-point plan per machine
                    ↓
INTERACT    →  What-If Simulator | Threshold Explorer | Box Plots
```

---

## 📊 Section Overview

| # | Section | Key Features |
|---|---|---|
| 1 | Setup & Data Simulation | 450 sensor readings, 5 failure profiles, anomaly detection |
| 2 | Data Input | Sliders for live readings, optional CSV upload |
| 3 | Analysis & Decision Engine | Color-coded fleet table, rule-based decision flags |
| 4 | Result Display | Trend charts, fleet dashboard, heatmap, anomaly scatter |
| 5 | LLM Suggestion Engine | Per-machine Claude recommendations, batch mode |
| 6 | Parameter Interaction | Multi-metric explorer, what-if simulator |
| 7 | Presentation Summary | Slide-ready KPI dashboard + talking points |

---

## ⚙️ Risk Scoring Logic

| Sensor | Max Points | Critical Threshold |
|---|---|---|
| Temperature (°C) | 35 | > 95°C |
| Vibration (mm/s) | 25 | > 6.0 mm/s |
| Runtime Hours | 20 | > 500 hrs |
| Pressure (bar) | 12 | > 9.0 bar |
| Error Count (24h) | 8 | > 8 errors |

**Risk Levels:** Low (0–24) · Medium (25–49) · High (50–74) · Critical (75–100)

---

## 🤖 Recommendation Engine

The advisor turns the risk analysis into a 5-point plan. By default it runs the **offline expert system** (rule-based, derived from the actual sensor readings — no API key, no internet). Optionally switch to **Claude** for natural-language generation. Both return the same structure:

1. **Root Cause** — what is likely causing elevated risk
2. **Immediate Action** — specific step to take right now
3. **Maintenance Plan** — recommended schedule for the next 7 days
4. **Estimated Downtime** — expected hours if maintenance is needed
5. **Risk If Ignored** — consequences without intervention

---

## 🖥️ Machine Profiles

| Machine | Profile | Key Issue |
|---|---|---|
| M-001 | Healthy | Baseline — all sensors normal |
| M-002 | Overheating | Temperature rises 0.9°C/day over 30 days |
| M-003 | Bearing Failure | Vibration spikes sharply in final 10 days |
| M-004 | Overdue Maintenance | High runtime + elevated pressure |
| M-005 | Cascading Failure | Error rate accelerates as machine degrades |

---

## ⚠️ Known Limitations

- Data is simulated — real deployment connects to MQTT/OPC-UA sensor streams
- Risk thresholds are hardcoded — could be learned from historical failure data
- LLM recommendations not persisted — a maintenance log DB needed for production
- No push alerting — SMS/email for Critical machines would add real-world value

---

## 🛠️ Tech Stack

`pandas` · `numpy` · `matplotlib` · `scikit-learn` · `ipywidgets` · `anthropic` *(optional)*

---

## 📋 Key Demo Moments (for presentation)

1. **M-005 risk trend** (Section 4) — dramatic spike in final days shows cascading failure
2. **Batch LLM mode** (Section 5) — click once, get Claude recommendations for all urgent machines
3. **What-If Simulator** (Section 6) — reduce M-002 temperature by 15°C and watch risk score drop
4. **Section 7** — run last for a slide-ready summary with live KPIs and fleet status
