# Generate a fully client-side static version of the app for GitHub Pages.
# Reuses the engine + precomputed data/charts from flask_app.py.
import json
import flask_app as A

# Maps (replace Python None key with "" for JS)
def jsmap(d):
    return json.dumps({(k if k is not None else ""): v for k, v in d.items()}, ensure_ascii=False)

IMMEDIATE   = jsmap(A._IMMEDIATE)
RISK_IGN    = jsmap(A._RISK_IF_IGNORED)
PLAN        = jsmap(A._PLAN)
DOWNTIME    = jsmap(A._DOWNTIME)
COLORS      = json.dumps(A.RISK_COLORS)
LATEST      = json.dumps({m: {k: float(v) for k, v in d.items()} for m, d in A.LATEST.items()})
FLEET       = json.dumps(A._fleet_rows(), ensure_ascii=False)
STATS       = A.STATS

HTML = """<!doctype html><html lang="en"><head><meta charset="utf-8">
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
 <div class="badge"><div class="n">__MACHINES__</div><div class="l">Machines</div></div>
 <div class="badge"><div class="n">__READINGS__</div><div class="l">Readings</div></div>
 <div class="badge"><div class="n">__ANOM__</div><div class="l">Anomalies</div></div>
 <div class="badge"><div class="n" style="color:#e74c3c">__CRIT__</div><div class="l">Critical</div></div>
 <div class="badge"><div class="n" style="color:#e67e22">__HIGH__</div><div class="l">High Risk</div></div>
 <div class="badge"><div class="n">__AVG__</div><div class="l">Avg Risk</div></div>
</div>

<div class="card">
 <h2>🎛️ Analyze a Reading <span class="note">(updates live as you type)</span></h2>
 <div class="grid">
  <div><label>Equipment</label>
   <select id="eq" onchange="prefill();run()">__OPTIONS__</select></div>
  <div><label>Temperature (°C)</label><input type="number" step="0.1" id="temperature" oninput="run()"></div>
  <div><label>Vibration (mm/s)</label><input type="number" step="0.1" id="vibration" oninput="run()"></div>
  <div><label>Runtime Hours</label><input type="number" step="1" id="runtime_hours" oninput="run()"></div>
  <div><label>Pressure (bar)</label><input type="number" step="0.1" id="pressure" oninput="run()"></div>
  <div><label>Errors (24h)</label><input type="number" step="1" id="error_count" oninput="run()"></div>
 </div>
 <div id="result"></div>
</div>

<div class="card">
 <h2>🏭 Fleet Status</h2>
 <table><thead><tr><th>Machine</th><th>Profile</th><th>Risk Score</th><th>Decision Flags</th></tr></thead>
 <tbody id="fleet"></tbody></table>
</div>

<div class="card"><h2>📊 Fleet Health Dashboard</h2><img src="data:image/png;base64,__CHART_DASH__"></div>
<div class="card"><h2>📈 30-Day Risk Trends</h2><img src="data:image/png;base64,__CHART_TRENDS__"></div>

<footer>Equipment Maintenance Decision System · by Omar · Knowledge Engineering Final Project · runs 100% in your browser, no server</footer>
</div>

<script>
const IMMEDIATE=__IMMEDIATE__, RISK_IGN=__RISK_IGN__, PLAN=__PLAN__, DOWNTIME=__DOWNTIME__,
      COLORS=__COLORS__, LATEST=__LATEST__, FLEET=__FLEET__;

function score(t,v,r,p,e){let s=0;
 if(t>95)s+=35;else if(t>85)s+=20;else if(t>75)s+=10;
 if(v>6)s+=25;else if(v>4.5)s+=15;else if(v>3)s+=8;
 if(r>500)s+=20;else if(r>350)s+=12;else if(r>200)s+=5;
 if(p>9)s+=12;else if(p>7.5)s+=6;
 if(e>8)s+=8;else if(e>4)s+=4;return Math.min(s,100);}
function level(s){return s>=75?'Critical':s>=50?'High':s>=25?'Medium':'Low';}
function findings(t,v,r,p,e){const rk={critical:0,high:1,watch:2};let f=[];
 if(t>95)f.push(['critical','temperature',`Temperature ${t.toFixed(0)}°C is critically high (>95°C), indicating a cooling failure or sustained overload.`]);
 else if(t>85)f.push(['high','temperature',`Temperature ${t.toFixed(0)}°C is elevated (>85°C), an early overheating trend.`]);
 else if(t>75)f.push(['watch','temperature',`Temperature ${t.toFixed(0)}°C is mildly above normal (>75°C).`]);
 if(v>6)f.push(['critical','vibration',`Vibration ${v.toFixed(1)} mm/s is severe (>6.0), a strong bearing-failure or imbalance signature.`]);
 else if(v>4.5)f.push(['high','vibration',`Vibration ${v.toFixed(1)} mm/s is high (>4.5), showing developing mechanical wear.`]);
 else if(v>3)f.push(['watch','vibration',`Vibration ${v.toFixed(1)} mm/s is slightly raised (>3.0).`]);
 if(r>500)f.push(['high','runtime',`${r.toFixed(0)} h since last service (>500) — well past the maintenance interval.`]);
 else if(r>350)f.push(['watch','runtime',`${r.toFixed(0)} h since last service (>350) — service window approaching.`]);
 if(p>9)f.push(['high','pressure',`Pressure ${p.toFixed(1)} bar exceeds the safe limit (>9.0).`]);
 else if(p>7.5)f.push(['watch','pressure',`Pressure ${p.toFixed(1)} bar is slightly high (>7.5).`]);
 if(e>8)f.push(['high','error',`${e.toFixed(0)} errors/24h (>8) indicate control-system instability.`]);
 else if(e>4)f.push(['watch','error',`${e.toFixed(0)} errors/24h (>4) — a rising fault count.`]);
 f.sort((a,b)=>rk[a[0]]-rk[b[0]]);return f;}
function decision(lv,t,v,r,p,e){let a=[];
 if(lv==='Critical')a.push('🔴 IMMEDIATE SHUTDOWN REQUIRED');
 if(t>90)a.push('🌡️ Check cooling system / reduce load');
 if(v>5)a.push('📳 Inspect bearings and mounting bolts');
 if(r>400)a.push('🔧 Schedule full maintenance (overdue)');
 if(p>8)a.push('⚠️ Check pressure relief valves');
 if(e>5)a.push('💻 Review error logs — possible sensor fault');
 if(!a.length)a.push('✅ No immediate action required');return a;}
function recommend(lv,t,v,r,p,e){const F=findings(t,v,r,p,e);const pr=F.length?F[0][1]:'';
 let root;if(F.length){root=F[0][2];if(F.length>1){const o=F.slice(1).map(x=>x[1]).join(', ');
   root+=` It is compounded by out-of-range ${o} readings, suggesting multi-factor degradation.`;}}
 else root='All sensors sit within their baseline ranges; no degradation signature is present.';
 return {'ROOT CAUSE':root,'IMMEDIATE ACTION':IMMEDIATE[pr],'MAINTENANCE PLAN':PLAN[lv]||PLAN['Low'],
  'ESTIMATED DOWNTIME':DOWNTIME[lv]||DOWNTIME['Low'],'RISK IF IGNORED':RISK_IGN[pr]};}

function val(id){return parseFloat(document.getElementById(id).value)||0;}
function prefill(){const m=document.getElementById('eq').value,d=LATEST[m];if(!d)return;
 for(const k in d)document.getElementById(k).value=d[k];}
function run(){
 const eq=document.getElementById('eq').value;
 const t=val('temperature'),v=val('vibration'),r=val('runtime_hours'),p=val('pressure'),e=val('error_count');
 const s=score(t,v,r,p,e),lv=level(s),c=COLORS[lv],fl=decision(lv,t,v,r,p,e),rc=recommend(lv,t,v,r,p,e);
 let h=`<div class="rec" style="border-left-color:${c}"><h3>${eq} — <span class="pill" style="background:${c}">${lv} · ${s}/100</span></h3>`;
 h+=`<div class="flags"><b>Decision flags:</b> `+fl.map(x=>`<span>${x}</span>`).join('')+`</div>`;
 h+=`<hr style="border:0;border-top:1px solid #e7edf2;margin:12px 0">`;
 let i=1;for(const k in rc){h+=`<p><b>${i}. ${k}:</b> ${rc[k]}</p>`;i++;}
 h+=`<div class="note">Generated by the offline maintenance expert system — no API key, no internet, runs in your browser.</div></div>`;
 document.getElementById('result').innerHTML=h;}
function fleetTable(){let h='';FLEET.forEach(r=>{h+=`<tr><td><b>${r.equipment_id}</b></td><td style="color:#666">${r.profile}</td>`+
  `<td><span class="bar"><div style="width:${r.risk_score}%;background:${r.color}"></div></span>`+
  `<span style="color:${r.color};font-weight:700">&nbsp;${r.risk_score}/100 · ${r.risk_level}</span></td>`+
  `<td style="font-size:12px;color:#555">${r.flags}</td></tr>`;});
 document.getElementById('fleet').innerHTML=h;}
prefill();run();fleetTable();
</script></body></html>"""

repl = {
    "__MACHINES__": str(STATS["machines"]), "__READINGS__": str(STATS["readings"]),
    "__ANOM__": str(STATS["anomalies"]), "__CRIT__": str(STATS["critical"]),
    "__HIGH__": str(STATS["high"]), "__AVG__": str(STATS["avg_risk"]),
    "__OPTIONS__": "".join(f'<option value="{m}">{m}</option>' for m in A.EQUIPMENT_IDS),
    "__CHART_DASH__": A.CHART_DASHBOARD, "__CHART_TRENDS__": A.CHART_TRENDS,
    "__IMMEDIATE__": IMMEDIATE, "__RISK_IGN__": RISK_IGN, "__PLAN__": PLAN,
    "__DOWNTIME__": DOWNTIME, "__COLORS__": COLORS, "__LATEST__": LATEST, "__FLEET__": FLEET,
}
for k, v in repl.items():
    HTML = HTML.replace(k, v)

import os
os.makedirs("../Omar/docs", exist_ok=True)
with open("../Omar/docs/index.html", "w", encoding="utf-8") as f:
    f.write(HTML)
print("Wrote ../Omar/docs/index.html  (", len(HTML), "bytes )")
