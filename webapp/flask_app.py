# ============================================================================
#  Equipment Maintenance Intelligent Decision System  —  Web App (Flask)
#  Author: Omar   |   Knowledge Engineering Final Project
#
#  Live web version of the Jupyter project. Runs 100% OFFLINE — no API key,
#  no internet, no external calls — so it works on PythonAnywhere's free tier
#  and anywhere in the world, including mainland China.
# ============================================================================
import io
import base64

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")                       # headless backend for a web server
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.colors import LinearSegmentedColormap
from sklearn.ensemble import IsolationForest
from flask import Flask, request, render_template_string

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------
EQUIPMENT_IDS    = ["M-001", "M-002", "M-003", "M-004", "M-005"]
DAYS             = 30
READINGS_PER_DAY = 3
RANDOM_SEED      = 42
np.random.seed(RANDOM_SEED)

RISK_COLORS = {"Low": "#2ecc71", "Medium": "#f39c12",
               "High": "#e67e22", "Critical": "#e74c3c"}

# ---------------------------------------------------------------------------
# RISK SCORING ENGINE  (identical thresholds to the notebook)
# ---------------------------------------------------------------------------
def compute_risk_score(temp, vibration, runtime_hours, pressure, error_count):
    score = 0
    if   temp > 95: score += 35
    elif temp > 85: score += 20
    elif temp > 75: score += 10
    if   vibration > 6.0: score += 25
    elif vibration > 4.5: score += 15
    elif vibration > 3.0: score += 8
    if   runtime_hours > 500: score += 20
    elif runtime_hours > 350: score += 12
    elif runtime_hours > 200: score += 5
    if   pressure > 9.0: score += 12
    elif pressure > 7.5: score += 6
    if   error_count > 8: score += 8
    elif error_count > 4: score += 4
    return min(score, 100)


def score_to_level(score):
    if   score >= 75: return "Critical"
    elif score >= 50: return "High"
    elif score >= 25: return "Medium"
    return "Low"


# ---------------------------------------------------------------------------
# DATA SIMULATION  (same five failure profiles as the notebook)
# ---------------------------------------------------------------------------
def simulate_equipment_data():
    records = []
    timestamps = pd.date_range("2024-05-01", periods=DAYS * READINGS_PER_DAY, freq="8h")
    profiles = {
        "M-001": dict(label="Healthy",            temp_base=62, temp_drift=0.0, vib_base=1.8, runtime_base=40,  pressure_base=5.2, error_base=0.2),
        "M-002": dict(label="Overheating",         temp_base=74, temp_drift=0.9, vib_base=2.4, runtime_base=90,  pressure_base=5.8, error_base=0.8),
        "M-003": dict(label="Bearing Failure",     temp_base=71, temp_drift=0.2, vib_base=3.5, runtime_base=180, pressure_base=6.3, error_base=1.5),
        "M-004": dict(label="Overdue Maintenance", temp_base=83, temp_drift=0.3, vib_base=4.0, runtime_base=460, pressure_base=7.8, error_base=4.0),
        "M-005": dict(label="Cascading Failure",   temp_base=78, temp_drift=0.6, vib_base=4.5, runtime_base=310, pressure_base=8.2, error_base=7.0),
    }
    for eq_id, p in profiles.items():
        for i, ts in enumerate(timestamps):
            day  = i // READINGS_PER_DAY
            frac = day / DAYS
            temp = p["temp_base"] + p["temp_drift"] * day + np.random.normal(0, 1.5)
            vib_extra = (day - 20) * 0.28 if (eq_id == "M-003" and day >= 20) else 0
            vibration = max(0, p["vib_base"] + vib_extra + np.random.normal(0, 0.25))
            err_rate = p["error_base"] * (1 + frac * 2.0) if eq_id == "M-005" else p["error_base"]
            runtime  = int(p["runtime_base"] + day * 8 + np.random.randint(0, 3))
            pressure = max(0, p["pressure_base"] + np.random.normal(0, 0.3))
            errors   = max(0, int(np.random.poisson(err_rate)))
            score    = compute_risk_score(temp, vibration, runtime, pressure, errors)
            records.append({
                "equipment_id": eq_id, "profile": p["label"], "timestamp": ts,
                "temperature": round(temp, 1), "vibration": round(vibration, 2),
                "runtime_hours": runtime, "pressure": round(pressure, 1),
                "error_count": errors, "risk_score": score, "risk_level": score_to_level(score),
            })
    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


def fleet_summary(df):
    latest = df.sort_values("timestamp").groupby("equipment_id").last().reset_index()
    avg = df.groupby("equipment_id")["risk_score"].mean().round(1).reset_index()
    avg.columns = ["equipment_id", "avg_risk_score"]
    return latest.merge(avg, on="equipment_id")


def generate_decision(row):
    actions = []
    if row["risk_level"] == "Critical":  actions.append("🔴 IMMEDIATE SHUTDOWN REQUIRED")
    if row["temperature"] > 90:          actions.append("🌡️ Check cooling system / reduce load")
    if row["vibration"] > 5:             actions.append("📳 Inspect bearings and mounting bolts")
    if row["runtime_hours"] > 400:       actions.append("🔧 Schedule full maintenance (overdue)")
    if row["pressure"] > 8:              actions.append("⚠️ Check pressure relief valves")
    if row["error_count"] > 5:           actions.append("💻 Review error logs — possible sensor fault")
    if not actions:                      actions.append("✅ No immediate action required")
    return actions


# ---------------------------------------------------------------------------
# OFFLINE EXPERT RECOMMENDATION ENGINE  (no API key, no internet)
# ---------------------------------------------------------------------------
_SEV_RANK = {"critical": 0, "high": 1, "watch": 2}

def _sensor_findings(row):
    temp, vib = float(row["temperature"]), float(row["vibration"])
    rt, pr, err = float(row["runtime_hours"]), float(row["pressure"]), float(row["error_count"])
    f = []
    if   temp > 95: f.append(("critical", "temperature", f"Temperature {temp:.0f}°C is critically high (>95°C), indicating a cooling failure or sustained overload."))
    elif temp > 85: f.append(("high",     "temperature", f"Temperature {temp:.0f}°C is elevated (>85°C), an early overheating trend."))
    elif temp > 75: f.append(("watch",    "temperature", f"Temperature {temp:.0f}°C is mildly above normal (>75°C)."))
    if   vib > 6.0: f.append(("critical", "vibration",   f"Vibration {vib:.1f} mm/s is severe (>6.0), a strong bearing-failure or imbalance signature."))
    elif vib > 4.5: f.append(("high",     "vibration",   f"Vibration {vib:.1f} mm/s is high (>4.5), showing developing mechanical wear."))
    elif vib > 3.0: f.append(("watch",    "vibration",   f"Vibration {vib:.1f} mm/s is slightly raised (>3.0)."))
    if   rt > 500:  f.append(("high",     "runtime",     f"{rt:.0f} h since last service (>500) — well past the maintenance interval."))
    elif rt > 350:  f.append(("watch",    "runtime",     f"{rt:.0f} h since last service (>350) — service window approaching."))
    if   pr > 9.0:  f.append(("high",     "pressure",    f"Pressure {pr:.1f} bar exceeds the safe limit (>9.0)."))
    elif pr > 7.5:  f.append(("watch",    "pressure",    f"Pressure {pr:.1f} bar is slightly high (>7.5)."))
    if   err > 8:   f.append(("high",     "error",       f"{err:.0f} errors/24h (>8) indicate control-system instability."))
    elif err > 4:   f.append(("watch",    "error",       f"{err:.0f} errors/24h (>4) — a rising fault count."))
    f.sort(key=lambda x: _SEV_RANK[x[0]])
    return f

_IMMEDIATE = {
    "temperature": "Reduce load and check the cooling/lubrication system (coolant level, fan, heat exchanger). If the temperature keeps climbing, shut the unit down to prevent thermal damage.",
    "vibration":   "Inspect bearings, couplings and mounting bolts for play or wear. Re-balance the rotor; stop the machine if vibration is in the severe band to avoid catastrophic bearing failure.",
    "runtime":     "Schedule the overdue service now — replace lubricant, filters and any wear parts that are past their interval.",
    "pressure":    "Check for blockages or valve faults, bring pressure back into the safe range, and confirm the relief valve is functioning.",
    "error":       "Pull the controller fault log, clear recoverable faults, and inspect sensors and wiring for intermittent signals.",
    None:          "No immediate action required — continue routine monitoring.",
}
_RISK_IF_IGNORED = {
    "temperature": "Continued overheating can warp components, break down lubricant, and lead to seizure or even a fire hazard.",
    "vibration":   "Unchecked vibration rapidly destroys bearings and can cause sudden, unplanned shaft or housing failure.",
    "runtime":     "Running past the service interval sharply raises the probability of a wear-related breakdown.",
    "pressure":    "Sustained over-pressure risks seal rupture, leaks, or hose/line failure.",
    "error":       "A rising error rate often precedes a controller or sensor failure that can halt the whole line.",
    None:          "Risk stays low; no significant short-term consequence is expected.",
}
_PLAN = {
    "Critical": "Day 0: take the machine offline for inspection. Days 1-2: replace the failing component identified above. Days 3-7: run-in test and confirm every sensor returns to baseline before resuming full production.",
    "High":     "Days 1-2: schedule a planned inspection at the next shift change. Days 3-5: replace worn parts and re-lubricate. Days 6-7: re-measure and confirm the risk score falls below 25.",
    "Medium":   "Within 7 days: perform standard preventive maintenance (lubrication, cleaning, fastener and sensor check) and re-baseline the flagged reading.",
    "Low":      "No special action — keep the routine 30-day preventive-maintenance cycle.",
}
_DOWNTIME = {
    "Critical": "8-24 hours (component replacement plus run-in test).",
    "High":     "2-6 hours (planned inspection and parts replacement).",
    "Medium":   "0.5-2 hours (routine preventive maintenance).",
    "Low":      "None expected.",
}

def generate_recommendation(row):
    level = row.get("risk_level", "Low")
    score = int(row.get("risk_score", 0))
    findings = _sensor_findings(row)
    primary = findings[0][1] if findings else None
    if findings:
        root = findings[0][2]
        if len(findings) > 1:
            others = ", ".join(s for _, s, _ in findings[1:])
            root += f" It is compounded by out-of-range {others} readings, suggesting multi-factor degradation."
    else:
        root = "All sensors sit within their baseline ranges; no degradation signature is present."
    return {
        "ROOT CAUSE": root,
        "IMMEDIATE ACTION": _IMMEDIATE[primary],
        "MAINTENANCE PLAN": _PLAN.get(level, _PLAN["Low"]),
        "ESTIMATED DOWNTIME": _DOWNTIME.get(level, _DOWNTIME["Low"]),
        "RISK IF IGNORED": _RISK_IF_IGNORED[primary],
    }


# ---------------------------------------------------------------------------
# BUILD DATA + CHARTS ONCE AT STARTUP (data is static, so cache the images)
# ---------------------------------------------------------------------------
def _fig_to_b64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=110, bbox_inches="tight")
    plt.close(fig)
    return base64.b64encode(buf.getvalue()).decode("ascii")


def build_dashboard_chart(df, summary):
    fig = plt.figure(figsize=(15, 9))
    fig.suptitle("Fleet Health Dashboard", fontsize=16, fontweight="bold", y=1.0)
    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    ax1 = fig.add_subplot(gs[0, 0])
    bars = ax1.bar(summary["equipment_id"], summary["risk_score"],
                   color=[RISK_COLORS[r] for r in summary["risk_level"]], edgecolor="white", linewidth=1.5)
    for bar, s in zip(bars, summary["risk_score"]):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.5, f"{int(s)}",
                 ha="center", va="bottom", fontsize=10, fontweight="bold")
    ax1.set_title("Current Risk Scores", fontweight="bold"); ax1.set_ylim(0, 110)
    ax1.axhline(75, color="#e74c3c", ls="--", alpha=0.7); ax1.axhline(50, color="#e67e22", ls="--", alpha=0.7)

    ax2 = fig.add_subplot(gs[0, 1])
    lc = df["risk_level"].value_counts()
    ax2.pie(lc.values, labels=lc.index, colors=[RISK_COLORS[l] for l in lc.index],
            autopct="%1.0f%%", startangle=90, textprops={"fontsize": 9})
    ax2.set_title("Risk Level Distribution", fontweight="bold")

    ax3 = fig.add_subplot(gs[0, 2])
    ac = df.groupby("equipment_id")["is_anomaly"].sum()
    ax3.bar(ac.index, ac.values, color="#9b59b6", alpha=0.85, edgecolor="white")
    ax3.set_title("Anomalies per Machine", fontweight="bold")

    ax4 = fig.add_subplot(gs[1, :])
    cols = ["temperature", "vibration", "pressure", "error_count", "risk_score"]
    hd = summary.set_index("equipment_id")[cols]
    hn = (hd - hd.min()) / (hd.max() - hd.min())
    cmap = LinearSegmentedColormap.from_list("risk", ["#2ecc71", "#f39c12", "#e74c3c"])
    im = ax4.imshow(hn.values, aspect="auto", cmap=cmap, vmin=0, vmax=1)
    ax4.set_xticks(range(len(cols))); ax4.set_xticklabels(cols, fontsize=10)
    ax4.set_yticks(range(len(EQUIPMENT_IDS))); ax4.set_yticklabels(EQUIPMENT_IDS)
    ax4.set_title("Sensor Heatmap (normalized — red = worst)", fontweight="bold")
    fig.colorbar(im, ax=ax4, fraction=0.012, label="Normalized")
    for i in range(len(EQUIPMENT_IDS)):
        for j in range(len(cols)):
            ax4.text(j, i, f"{hd.values[i, j]:.1f}", ha="center", va="center",
                     fontsize=8, color="white" if hn.values[i, j] > 0.5 else "black")
    return _fig_to_b64(fig)


def build_trends_chart(df):
    fig, axes = plt.subplots(2, 3, figsize=(15, 7.5), constrained_layout=True)
    fig.suptitle("Risk Score Trends (30 Days)", fontsize=14, fontweight="bold")
    for ax, eq in zip(axes.flat, EQUIPMENT_IDS):
        sub = df[df["equipment_id"] == eq].sort_values("timestamp").copy()
        sub["roll"] = sub["risk_score"].rolling(6, min_periods=1).mean()
        ax.fill_between(sub["timestamp"], sub["risk_score"], alpha=0.15, color="#3498db")
        ax.plot(sub["timestamp"], sub["risk_score"], alpha=0.4, lw=0.8, color="#3498db")
        ax.plot(sub["timestamp"], sub["roll"], lw=2, color="#2980b9")
        ax.axhspan(75, 100, alpha=0.08, color="#e74c3c"); ax.axhspan(50, 75, alpha=0.08, color="#e67e22")
        latest = sub.iloc[-1]
        ax.set_title(f'{eq} — {latest["profile"]}\n{int(latest["risk_score"])}/100 ({latest["risk_level"]})',
                     fontsize=9, color=RISK_COLORS[latest["risk_level"]])
        ax.set_ylim(0, 100); ax.tick_params(axis="x", rotation=30, labelsize=7)
    axes.flat[-1].set_visible(False)
    return _fig_to_b64(fig)


DF = simulate_equipment_data()
_features = ["temperature", "vibration", "runtime_hours", "pressure", "error_count"]
_iso = IsolationForest(contamination=0.07, random_state=RANDOM_SEED)
DF["anomaly"] = _iso.fit_predict(DF[_features])
DF["is_anomaly"] = DF["anomaly"] == -1
SUMMARY = fleet_summary(DF)
LATEST = {r["equipment_id"]: {k: r[k] for k in _features} for _, r in SUMMARY.iterrows()}

CHART_DASHBOARD = build_dashboard_chart(DF, SUMMARY)
CHART_TRENDS = build_trends_chart(DF)
STATS = dict(
    machines=len(SUMMARY), readings=len(DF), anomalies=int(DF["is_anomaly"].sum()),
    critical=int((SUMMARY["risk_level"] == "Critical").sum()),
    high=int((SUMMARY["risk_level"] == "High").sum()),
    avg_risk=round(DF["risk_score"].mean()),
)

# ---------------------------------------------------------------------------
# FLASK APP
# ---------------------------------------------------------------------------
app = Flask(__name__)

PAGE = """
<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Equipment Maintenance Decision System — Omar</title>
<style>
 *{box-sizing:border-box} body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#eef1f5;color:#222}
 .wrap{max-width:1040px;margin:auto;padding:18px}
 header{background:linear-gradient(135deg,#1a252f,#2c3e50 60%,#34495e);color:#fff;border-radius:14px;padding:26px 30px;box-shadow:0 4px 20px rgba(0,0,0,.25)}
 header .tag{font-size:11px;letter-spacing:4px;opacity:.55;text-transform:uppercase}
 header h1{margin:6px 0 6px;font-size:26px} header p{margin:0;opacity:.82;font-size:14px}
 .badges{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}
 .badge{flex:1;min-width:140px;background:#fff;border-radius:10px;padding:14px 16px;text-align:center;box-shadow:0 2px 10px rgba(0,0,0,.07)}
 .badge .n{font-size:26px;font-weight:800} .badge .l{font-size:11px;color:#777;text-transform:uppercase;letter-spacing:.5px;margin-top:3px}
 .card{background:#fff;border-radius:12px;padding:20px 24px;margin:16px 0;box-shadow:0 2px 12px rgba(0,0,0,.07)}
 h2{font-size:17px;margin:0 0 14px;color:#2c3e50}
 label{display:block;font-size:13px;font-weight:600;margin:10px 0 4px;color:#444}
 select,input[type=number]{width:100%;padding:9px 11px;border:1px solid #cfd6dd;border-radius:8px;font-size:14px}
 .grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}
 button{margin-top:16px;background:#2980b9;color:#fff;border:0;border-radius:8px;padding:12px 22px;font-size:15px;font-weight:600;cursor:pointer}
 button:hover{background:#2471a3}
 table{width:100%;border-collapse:collapse;font-size:13px} th{background:#2c3e50;color:#fff;padding:10px 12px;text-align:left;font-size:12px}
 td{padding:10px 12px;border-bottom:1px solid #f0f0f0}
 .pill{display:inline-block;padding:2px 10px;border-radius:20px;color:#fff;font-size:12px;font-weight:700}
 .bar{background:#e8e8e8;border-radius:6px;height:16px;width:150px;overflow:hidden;display:inline-block;vertical-align:middle}
 .bar>div{height:100%}
 img{width:100%;border-radius:8px;border:1px solid #eee}
 .rec{border-left:5px solid #2980b9;background:#f8fafc;border-radius:6px;padding:14px 18px;margin-top:14px}
 .rec h3{margin:0 0 10px;font-size:16px} .rec b{color:#2c3e50}
 .rec p{margin:7px 0;font-size:14px;line-height:1.55}
 .flags span{display:inline-block;background:#eef2f6;border-radius:6px;padding:3px 9px;margin:2px;font-size:12px}
 footer{text-align:center;color:#8a97a5;font-size:12px;margin:24px 0 8px}
 .note{font-size:12px;color:#888;margin-top:6px}
</style></head><body><div class="wrap">

<header>
 <div class="tag">Knowledge Engineering · Final Project</div>
 <h1>🔧 Equipment Maintenance Intelligent Decision System</h1>
 <p>Real-time risk scoring · anomaly detection · plain-English maintenance advice — by <b>Omar</b></p>
</header>

<div class="badges">
 <div class="badge"><div class="n">{{s.machines}}</div><div class="l">Machines</div></div>
 <div class="badge"><div class="n">{{s.readings}}</div><div class="l">Readings</div></div>
 <div class="badge"><div class="n">{{s.anomalies}}</div><div class="l">Anomalies</div></div>
 <div class="badge"><div class="n" style="color:#e74c3c">{{s.critical}}</div><div class="l">Critical</div></div>
 <div class="badge"><div class="n" style="color:#e67e22">{{s.high}}</div><div class="l">High Risk</div></div>
 <div class="badge"><div class="n">{{s.avg_risk}}</div><div class="l">Avg Risk</div></div>
</div>

<div class="card">
 <h2>🎛️ Analyze a Reading</h2>
 <form method="post" action="/">
  <div class="grid">
   <div><label>Equipment</label>
    <select name="equipment_id" id="eq" onchange="prefill()">
     {% for m in machines %}<option value="{{m}}" {% if sel and sel.equipment_id==m %}selected{% endif %}>{{m}}</option>{% endfor %}
    </select></div>
   <div><label>Temperature (°C)</label><input type="number" step="0.1" name="temperature" id="temperature" value="{{sel.temperature if sel else 75}}"></div>
   <div><label>Vibration (mm/s)</label><input type="number" step="0.1" name="vibration" id="vibration" value="{{sel.vibration if sel else 3.0}}"></div>
   <div><label>Runtime Hours</label><input type="number" step="1" name="runtime_hours" id="runtime_hours" value="{{sel.runtime_hours if sel else 200}}"></div>
   <div><label>Pressure (bar)</label><input type="number" step="0.1" name="pressure" id="pressure" value="{{sel.pressure if sel else 6.0}}"></div>
   <div><label>Errors (24h)</label><input type="number" step="1" name="error_count" id="error_count" value="{{sel.error_count if sel else 2}}"></div>
  </div>
  <button type="submit">▶ Analyze & Recommend</button>
  <span class="note">Prefilled with each machine's latest reading. Edit any value to run a what-if.</span>
 </form>

 {% if result %}
 <div class="rec" style="border-left-color:{{result.color}}">
  <h3>{{result.equipment_id}} —
   <span class="pill" style="background:{{result.color}}">{{result.risk_level}} · {{result.score}}/100</span></h3>
  <div class="flags"><b>Decision flags:</b> {% for f in result.flags %}<span>{{f}}</span>{% endfor %}</div>
  <hr style="border:0;border-top:1px solid #e7edf2;margin:12px 0">
  {% for k,v in result.rec.items() %}<p><b>{{loop.index}}. {{k}}:</b> {{v}}</p>{% endfor %}
  <div class="note">Generated by the offline maintenance expert system — no API key, no internet.</div>
 </div>
 {% endif %}
</div>

<div class="card">
 <h2>🏭 Fleet Status</h2>
 <table><thead><tr><th>Machine</th><th>Profile</th><th>Risk Score</th><th>Decision Flags</th></tr></thead><tbody>
 {% for r in fleet %}
  <tr><td><b>{{r.equipment_id}}</b></td><td style="color:#666">{{r.profile}}</td>
   <td><span class="bar"><div style="width:{{r.risk_score}}%;background:{{r.color}}"></div></span>
       <span style="color:{{r.color}};font-weight:700">&nbsp;{{r.risk_score}}/100 · {{r.risk_level}}</span></td>
   <td style="font-size:12px;color:#555">{{r.flags}}</td></tr>
 {% endfor %}
 </tbody></table>
</div>

<div class="card"><h2>📊 Fleet Health Dashboard</h2><img src="data:image/png;base64,{{chart_dashboard}}"></div>
<div class="card"><h2>📈 30-Day Risk Trends</h2><img src="data:image/png;base64,{{chart_trends}}"></div>

<footer>Equipment Maintenance Decision System · by Omar · Knowledge Engineering Final Project · runs 100% offline</footer>
</div>

<script>
 var LATEST = {{ latest_json|safe }};
 function prefill(){
   var m = document.getElementById('eq').value, d = LATEST[m]; if(!d) return;
   for (var k in d){ var el = document.getElementById(k); if(el) el.value = d[k]; }
 }
</script>
</body></html>
"""


def _fleet_rows():
    rows = []
    for _, r in SUMMARY.sort_values("risk_score", ascending=False).iterrows():
        rows.append({
            "equipment_id": r["equipment_id"], "profile": r["profile"],
            "risk_score": int(r["risk_score"]), "risk_level": r["risk_level"],
            "color": RISK_COLORS[r["risk_level"]],
            "flags": " · ".join(generate_decision(r)),
        })
    return rows


@app.route("/", methods=["GET", "POST"])
def index():
    import json
    result = None
    sel = None
    if request.method == "POST":
        try:
            sel = {
                "equipment_id": request.form.get("equipment_id", "M-001"),
                "temperature": float(request.form.get("temperature", 75)),
                "vibration": float(request.form.get("vibration", 3.0)),
                "runtime_hours": float(request.form.get("runtime_hours", 200)),
                "pressure": float(request.form.get("pressure", 6.0)),
                "error_count": float(request.form.get("error_count", 2)),
            }
            score = compute_risk_score(sel["temperature"], sel["vibration"],
                                       sel["runtime_hours"], sel["pressure"], sel["error_count"])
            level = score_to_level(score)
            row = dict(sel, risk_score=score, risk_level=level)
            result = {
                "equipment_id": sel["equipment_id"], "score": score, "risk_level": level,
                "color": RISK_COLORS[level], "flags": generate_decision(row),
                "rec": generate_recommendation(row),
            }
        except (ValueError, TypeError):
            result = None
    return render_template_string(
        PAGE, s=STATS, machines=EQUIPMENT_IDS, fleet=_fleet_rows(),
        chart_dashboard=CHART_DASHBOARD, chart_trends=CHART_TRENDS,
        result=result, sel=sel, latest_json=json.dumps(LATEST),
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
