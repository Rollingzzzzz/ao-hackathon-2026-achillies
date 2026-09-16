"""Self-contained NOC dashboard generator.

Emits out/dashboard.html with all data and charts embedded (base64 PNG),
so it opens offline from file:// too. Action buttons talk to the optional
local API server (serve.py) when present; without the server the dashboard
is a static report.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path

SEV_COLORS = {5: "#ff5470", 4: "#ffb454", 3: "#f5f760", 2: "#59c2ff", 1: "#8b949e"}

TEMPLATE = """<!doctype html>
<html lang="tr"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>AlarmStorm — Nöbetçi Konsolu</title>
<style>
:root{--bg:#0b0d12;--panel:#12151d;--panel2:#171b25;--line:#232a38;--fg:#d6deeb;--dim:#8b949e;--acc:#00e5a0;--red:#ff5470;--amber:#ffb454;--blue:#59c2ff}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--bg);color:var(--fg);font:14px/1.5 "Segoe UI",system-ui,sans-serif;padding:22px}
h1{font-size:21px;letter-spacing:.5px}
h2{font-size:15px;margin:26px 0 12px;color:var(--dim);text-transform:uppercase;letter-spacing:1.5px}
.sub{color:var(--dim);font-size:12.5px;margin-top:2px}
.chips{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0 4px}
.chip{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px 16px}
.chip b{font-size:19px;display:block}
.chip span{color:var(--dim);font-size:11.5px;text-transform:uppercase;letter-spacing:1px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(430px,1fr));gap:16px}
.card{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--sev);border-radius:12px;padding:16px 18px;display:flex;flex-direction:column;gap:10px}
.chead{display:flex;justify-content:space-between;align-items:flex-start;gap:10px}
.cid{font-size:12px;color:var(--dim);letter-spacing:1px}
.ctitle{font-size:15.5px;font-weight:600;margin-top:2px}
.badge{border-radius:20px;padding:2px 10px;font-size:11px;letter-spacing:.5px;white-space:nowrap}
.b-sev{background:color-mix(in srgb,var(--sev) 18%,transparent);color:var(--sev);border:1px solid var(--sev)}
.b-pattern{background:#1c2230;color:var(--blue);border:1px solid #2a3550}
.meta{display:flex;gap:14px;flex-wrap:wrap;color:var(--dim);font-size:12.5px}
.meta b{color:var(--fg)}
.hyp{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:10px 12px;font-size:13px}
.hyp .lbl{color:var(--acc);font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px}
.evd{margin:6px 0 0 0;padding-left:16px;font-size:12.5px;color:#b9c4d4}
.evd li{margin:3px 0}
details{font-size:12.5px}
details summary{cursor:pointer;color:var(--blue);margin-top:4px;user-select:none}
.cntr{background:#141824;border:1px dashed #2a3550;border-radius:8px;padding:8px 10px;margin-top:6px;font-size:12px;color:#b9c4d4}
.cntr b{color:var(--amber)}
.svc{display:inline-block;background:#1c2230;border:1px solid #2a3550;border-radius:6px;padding:1px 7px;font-size:11.5px;margin:2px 3px 0 0;color:#aeb8cc}
.svc b{color:var(--fg)}
img.tl{width:100%;border-radius:8px;border:1px solid var(--line);margin-top:4px}
.act{background:var(--panel2);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.act .lbl{color:var(--amber);font-size:11px;text-transform:uppercase;letter-spacing:1px;margin-bottom:4px}
.act .owner{font-weight:600}
.status{display:inline-block;border-radius:6px;padding:1px 8px;font-size:11.5px;font-weight:600}
.st-acik{background:#3a1f27;color:var(--red)}
.st-islemde{background:#3a331a;color:var(--amber)}
.st-kapali{background:#153529;color:var(--acc)}
.btns{display:flex;gap:6px;margin-top:8px}
button{background:#1c2230;color:var(--fg);border:1px solid #2a3550;border-radius:7px;padding:4px 12px;font-size:12px;cursor:pointer}
button:hover{border-color:var(--blue)}
button:disabled{opacity:.35;cursor:default}
.hist{font-size:11px;color:var(--dim);margin-top:6px}
table{border-collapse:collapse;width:100%;font-size:12.5px}
th,td{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left}
th{color:var(--dim);font-size:11px;text-transform:uppercase;letter-spacing:1px}
.bar{height:8px;background:#1c2230;border-radius:4px;overflow:hidden;min-width:120px}
.bar i{display:block;height:100%;background:var(--blue)}
.note{color:var(--dim);font-size:12px;margin-top:10px}
.ok{color:var(--acc)}
</style></head><body>
<h1>⚡ AlarmStorm — Nöbetçi Konsolu</h1>
<div class="sub">10 Eylül 2026, 01:30–03:30 · S-A1 Alarm Fırtınası · <span id="gen"></span></div>
<div class="chips" id="chips"></div>
<img src="data:image/png;base64,__GLOBAL__" style="width:100%;border-radius:10px;border:1px solid var(--line);margin-top:8px">
<h2>Olay Kartları</h2>
<div class="grid" id="cards"></div>
<h2>Gürültü Denetimi — Her Alarmın Gerekçesi</h2>
<img src="data:image/png;base64,__NOISE__" style="width:100%;border-radius:10px;border:1px solid var(--line)">
<div id="noise" style="margin-top:12px"></div>
<div class="note" id="srvnote"></div>
<script>
const CARDS = __CARDS__;
const NOISE = __NOISED__;
const totals = __TOTALS__;
const gen = new Date();
document.getElementById("gen").textContent = gen.toLocaleString("tr-TR");

const chips = document.getElementById("chips");
const reduction = "1:" + Math.round(totals.total_alarms / Math.max(1, totals.event_count));
[[totals.total_alarms,"toplam alarm"],[totals.event_count,"olay kartı"],[reduction,"indirgeme oranı"],
 [totals.event_alarms,"olaya bağlanan"],[totals.noise_alarms,"gürültü (gerekçeli)"]].forEach(([v,l])=>{
  const d=document.createElement("div");d.className="chip";d.innerHTML=`<b>${v}</b><span>${l}</span>`;chips.appendChild(d);
});

const cardsEl = document.getElementById("cards");
let actions = {};
function render(){
  cardsEl.innerHTML = "";
  CARDS.forEach(c => {
    const a = actions[c.id] || {status:"açık", history:[]};
    const st = a.status, cls = st==="açık"?"st-acik":st==="işlemde"?"st-islemde":"st-kapali";
    const el = document.createElement("div");
    el.className = "card"; el.style.setProperty("--sev", SEVC[c.severity]);
    el.innerHTML = `
      <div class="chead">
        <div><div class="cid">${c.id} · ${c.root_kind_label.toUpperCase()}</div><div class="ctitle">${c.title}</div></div>
        <div style="display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end">
          <span class="badge b-sev">SEV ${c.severity}</span><span class="badge b-pattern">${c.pattern}</span>
        </div>
      </div>
      <div class="meta"><span>⏱ <b>${c.start} – ${c.end}</b></span><span>🔔 <b>${c.alarm_count}</b> alarm</span></div>
      <img class="tl" src="data:image/png;base64,${CHARTS[c.id]}">
      <div class="hyp"><div class="lbl">Kök Neden Hipotezi</div>${c.root_cause.hypothesis}
        <ul class="evd">${c.root_cause.evidence.map(e=>`<li>${e}</li>`).join("")}</ul>
        <details><summary>Karşı olasılıklar (${c.root_cause.counter_hypotheses.length})</summary>
          ${c.root_cause.counter_hypotheses.map(k=>`<div class="cntr"><b>${k.name}</b> (skor ${k.score}) — elenme gerekçesi: ${k.why_rejected}</div>`).join("") || '<div class="cntr">Belirgin alternatif aday yok.</div>'}
        </details>
      </div>
      <div><span style="color:var(--dim);font-size:11px;text-transform:uppercase;letter-spacing:1px">Etkilenen servisler</span><br>
        ${c.affected_top.map(([s,n])=>`<span class="svc">${s} <b>${n}</b></span>`).join("")}</div>
      <div class="act"><div class="lbl">Önerilen İlk Aksiyon</div>
        <span class="owner">👤 ${c.first_action.owner}</span> — ${c.first_action.action}
        <div style="margin-top:8px;display:flex;align-items:center;gap:10px">
          <span class="status ${cls}">${st.toUpperCase()}</span>
          <div class="btns">
            <button data-id="${c.id}" data-st="işlemde" ${st!=="açık"?"disabled":""}>▶ İşleme Al</button>
            <button data-id="${c.id}" data-st="kapalı" ${st==="kapalı"?"disabled":""}>✔ Kapat</button>
            <button data-id="${c.id}" data-st="açık" ${st==="açık"?"disabled":""}>↺ Yeniden Aç</button>
          </div>
        </div>
        <div class="hist">${(a.history||[]).slice(-6).map(h=>`· ${h.at.replace("T"," ")} → ${h.to}`).join(" &nbsp; ")}</div>
      </div>`;
    cardsEl.appendChild(el);
  });
  cardsEl.querySelectorAll("button[data-id]").forEach(b=>{
    b.onclick = async () => {
      try{
        const r = await fetch("/api/actions", {method:"POST", headers:{"Content-Type":"application/json"},
          body: JSON.stringify({id:b.dataset.id, status:b.dataset.st})});
        if(r.ok){ actions = await r.json(); render(); }
        else alert("Aksiyon sunucusuna ulaşılamadı (serve.py çalışıyor mu?)");
      }catch(e){ alert("Aksiyon sunucusu kapalı — statik görünüm. Sunucu: python serve.py"); }
    };
  });
}

async function loadActions(){
  try{ const r = await fetch("/api/actions"); if(r.ok){ actions = await r.json(); } }catch(e){}
  document.getElementById("srvnote").innerHTML = Object.keys(actions).length
    ? '<span class="ok">●</span> Aksiyon sunucusu bağlı — kart durumları canlı güncelleniyor.'
    : '○ Aksiyon sunucusu kapalı (statik görünüm). Canlı takip için: <code>python serve.py</code> → http://localhost:8787';
  render();
}

const nz = document.getElementById("noise");
let rows = Object.entries(NOISE.reason_counts).sort((a,b)=>b[1]-a[1]).map(([k,v])=>
  `<tr><td>${k}</td><td>${v}</td><td><div class="bar"><i style="width:${100*v/totals.noise_alarms}%"></i></div></td></tr>`).join("");
const per = Object.entries(NOISE.per_type).sort((a,b)=>b[1]-a[1]).slice(0,12).map(([k,v])=>
  `<span class="svc">${k} <b>${v}</b></span>`).join("");
nz.innerHTML = `<table><tr><th>Eleme gerekçesi</th><th>Alarm</th><th>Payı</th></tr>${rows}</table>
<div style="margin-top:10px"><span style="color:var(--dim);font-size:11px;text-transform:uppercase;letter-spacing:1px">Elenen alarm tipleri (ilk 12)</span><br>${per}</div>
<div class="note">Tam liste: <code>out/noise_audit.json</code> — her elenen alarm kimliği, gerekçesiyle kayıtlıdır.</div>`;
loadActions();
</script></body></html>
"""


def b64(path: Path) -> str:
    return base64.b64encode(path.read_bytes()).decode("ascii")


def generate_dashboard(out_dir: Path, cards: list[dict], noise_meta: dict, totals: dict) -> Path:
    charts = out_dir / "charts"
    na = json.loads((out_dir / "noise_audit.json").read_text(encoding="utf-8"))
    html = (
        TEMPLATE
        .replace("__GLOBAL__", b64(charts / "global_timeline.png"))
        .replace("__NOISE__", b64(charts / "noise_audit.png"))
        .replace("__CARDS__", json.dumps(cards, ensure_ascii=False))
        .replace("__NOISED__", json.dumps(
            {"reason_counts": noise_meta, "per_type": na.get("per_type", {})},
            ensure_ascii=False))
        .replace("__TOTALS__", json.dumps(totals, ensure_ascii=False))
    )
    # chart b64 map
    chart_map = {c["id"]: b64(charts / f'{c["id"]}_timeline.png') for c in cards}
    html = html.replace("<script>", "<script>const CHARTS=" + json.dumps(chart_map) + ";\nconst SEVC=" + json.dumps(SEV_COLORS) + ";\n", 1)
    p = out_dir / "dashboard.html"
    tmp = p.with_suffix(".html.tmp")
    tmp.write_text(html, encoding="utf-8")
    tmp.replace(p)
    return p
