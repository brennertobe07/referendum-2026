"""
make_publication.py
-------------------
Builds a self-contained one-page visual brief (HTML, inline SVG charts — no
external dependencies) from the Phase 4/5 analysis outputs.

Reads:  analysis\\LTV2026_Ref_Analysis.xlsx (sheets) + ENR summary.json
Writes: analysis\\Referendum2026_Summary.html   (open in a browser; print to PDF)

PDF (single US Letter page, no browser header/footer) — the print CSS uses
zoom: 0.70 so it fits one page. Generate with a FRESH Edge profile to avoid a
stale-cache 2-page result:
    msedge --headless --disable-gpu --user-data-dir="%TEMP%\\ghpdf" ^
      --print-to-pdf="analysis\\Referendum2026_Summary.pdf" ^
      "file:///.../analysis/Referendum2026_Summary.html"
Confirm with: python -c "from pypdf import PdfReader; print(len(PdfReader('....pdf').pages))"
"""
import json
from pathlib import Path
import pandas as pd

PROJ = Path(r"C:\DPVA_Projects\Referendum2026")
XLSX = PROJ / "analysis" / "LTV2026_Ref_Analysis.xlsx"
ENR = Path(r"C:\Scripts\Python\Python_ElectionResults\april-referendum-enr\data\summary.json")
OUT = PROJ / "analysis" / "Referendum2026_Summary.html"

INK = "#102a43"
BLUE = "#2b6cb0"
LBLUE = "#9fc0ea"
YES = "#2b6cb0"
NO = "#c05a6e"
DEM = "#2b6cb0"
REP = "#c0504d"
IND = "#9aa3ad"
GRID = "#dde3ea"


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg_result(yes_pct, no_pct, w=720, h=58):
    yw = w * yes_pct / 100.0
    return f"""<svg viewBox="0 0 {w} {h}" width="100%" role="img">
  <rect x="0" y="8" width="{w}" height="34" rx="6" fill="{NO}"/>
  <rect x="0" y="8" width="{yw:.1f}" height="34" rx="6" fill="{YES}"/>
  <text x="12" y="30" fill="#fff" font-size="16" font-weight="700">YES {yes_pct}%</text>
  <text x="{w-12}" y="30" fill="#fff" font-size="16" font-weight="700" text-anchor="end">NO {no_pct}%</text>
</svg>"""


def svg_grouped(cats, s1, s2, l1, l2, w=440, h=250, ymax=80):
    pad_l, pad_b, pad_t = 34, 34, 14
    cw = (w - pad_l - 8) / len(cats)
    bw = cw * 0.34
    def y(v): return pad_t + (h - pad_t - pad_b) * (1 - v / ymax)
    bars, labels = [], []
    for i, c in enumerate(cats):
        x0 = pad_l + i * cw + cw * 0.12
        bars.append(f'<rect x="{x0:.1f}" y="{y(s1[i]):.1f}" width="{bw:.1f}" height="{y(0)-y(s1[i]):.1f}" fill="{BLUE}"/>')
        bars.append(f'<rect x="{x0+bw:.1f}" y="{y(s2[i]):.1f}" width="{bw:.1f}" height="{y(0)-y(s2[i]):.1f}" fill="{LBLUE}"/>')
        labels.append(f'<text x="{pad_l+i*cw+cw/2:.1f}" y="{h-pad_b+14}" font-size="9" text-anchor="middle" fill="{INK}">{esc(c)}</text>')
    grid = "".join(f'<line x1="{pad_l}" y1="{y(g):.1f}" x2="{w}" y2="{y(g):.1f}" stroke="{GRID}"/><text x="{pad_l-4}" y="{y(g)+3:.1f}" font-size="8" text-anchor="end" fill="#7b8794">{g}</text>' for g in range(0, ymax + 1, 20))
    leg = f'<rect x="{pad_l}" y="2" width="10" height="10" fill="{BLUE}"/><text x="{pad_l+14}" y="11" font-size="9" fill="{INK}">{l1}</text><rect x="{pad_l+90}" y="2" width="10" height="10" fill="{LBLUE}"/><text x="{pad_l+104}" y="11" font-size="9" fill="{INK}">{l2}</text>'
    return f'<svg viewBox="0 0 {w} {h}" width="100%" role="img">{grid}{"".join(bars)}{"".join(labels)}{leg}</svg>'


def svg_bars(labels, vals, colors, w=440, h=250, ymax=None, suffix=""):
    ymax = ymax or (max(vals) * 1.15)
    pad_l, pad_b, pad_t = 34, 34, 12
    cw = (w - pad_l - 8) / len(labels)
    bw = cw * 0.55
    def y(v): return pad_t + (h - pad_t - pad_b) * (1 - v / ymax)
    bars = []
    for i, lab in enumerate(labels):
        x0 = pad_l + i * cw + (cw - bw) / 2
        col = colors[i] if isinstance(colors, list) else colors
        bars.append(f'<rect x="{x0:.1f}" y="{y(vals[i]):.1f}" width="{bw:.1f}" height="{y(0)-y(vals[i]):.1f}" rx="2" fill="{col}"/>')
        bars.append(f'<text x="{x0+bw/2:.1f}" y="{y(vals[i])-4:.1f}" font-size="9.5" font-weight="700" text-anchor="middle" fill="{INK}">{vals[i]:g}{suffix}</text>')
        bars.append(f'<text x="{pad_l+i*cw+cw/2:.1f}" y="{h-pad_b+14}" font-size="9" text-anchor="middle" fill="{INK}">{esc(lab)}</text>')
    return f'<svg viewBox="0 0 {w} {h}" width="100%" role="img">{"".join(bars)}</svg>'


def svg_donut(items, colors, w=250, h=250):
    import math
    cx, cy, r, rin = w / 2, h / 2, 95, 52
    total = sum(v for _, v in items)
    a0, segs, leg = -math.pi / 2, [], []
    for i, (lab, v) in enumerate(items):
        a1 = a0 + 2 * math.pi * v / total
        large = 1 if (a1 - a0) > math.pi else 0
        x0, y0 = cx + r * math.cos(a0), cy + r * math.sin(a0)
        x1, y1 = cx + r * math.cos(a1), cy + r * math.sin(a1)
        segs.append(f'<path d="M {x0:.1f} {y0:.1f} A {r} {r} 0 {large} 1 {x1:.1f} {y1:.1f} L {cx} {cy} Z" fill="{colors[i]}"/>')
        leg.append((lab, v / total * 100, colors[i]))
        a0 = a1
    legend = "".join(f'<rect x="6" y="{8+i*18}" width="11" height="11" fill="{c}"/><text x="22" y="{18+i*18}" font-size="10" fill="{INK}">{esc(l)} — {p:.1f}%</text>' for i, (l, p, c) in enumerate(leg))
    return f'<svg viewBox="0 0 {w+150} {h}" width="100%" role="img">{"".join(segs)}<circle cx="{cx}" cy="{cy}" r="{rin}" fill="#fff"/><g transform="translate({w},70)">{legend}</g></svg>'


def main():
    s = json.load(open(ENR))
    age = pd.read_excel(XLSX, "5b_age")
    vh = pd.read_excel(XLSX, "5d_votehistory")
    party = pd.read_excel(XLSX, "5g_party")
    method = pd.read_excel(XLSX, "5e_method_by_age")
    gen = pd.read_excel(XLSX, "5c_gender")
    strong = pd.read_excel(XLSX, "5f_strong_yes")
    weak = pd.read_excel(XLSX, "5f_weak_yes")

    age = age[age.age_band != "Unknown"]
    cats = age.age_band.tolist()
    ref = age.turnout_pct.tolist()
    base = age.baseline_2025G_pct.tolist()

    m = {c: int(method[c].sum()) for c in ["Polls", "AB_Inperson", "AB_Mail", "AB_Other"]}
    donut_items = [("Election day", m["Polls"]), ("In-person early", m["AB_Inperson"]), ("Mail", m["AB_Mail"])]

    pv = party.set_index("party_bucket")
    pbars_lab = ["Dem", "Rep"]
    pbars_val = [round(float(pv.loc[b, "turnout_pct"]), 1) for b in pbars_lab]
    dem_reg = float(pv.loc["Dem", "registered"]) / 1e6
    rep_reg = float(pv.loc["Rep", "registered"]) / 1e6
    dem_share = round(float(pv.loc["Dem", "share_of_voters_pct"]))
    rep_share = round(float(pv.loc["Rep", "share_of_voters_pct"]))

    vh = vh.sort_values("generals_voted_of_4")
    vh_lab = [f"{int(x)}-of-4" for x in vh.generals_voted_of_4]
    vh_val = [round(float(x), 1) for x in vh.pct]

    chart_age = svg_grouped(cats, ref, base, "Referendum", "2025 General")
    chart_method = svg_donut(donut_items, [BLUE, LBLUE, "#cbd6e6"])
    chart_party = svg_bars(pbars_lab, pbars_val, [DEM, REP], ymax=70, suffix="%")
    chart_vh = svg_bars(vh_lab, vh_val, [NO, "#d99", "#cbd5e0", LBLUE, BLUE], ymax=65, suffix="%")

    def loc_rows(df):
        return "".join(
            f"<tr><td>{esc(r['name'].title())}</td><td class='num'>{r['yes_pct']:.0f}%</td>"
            f"<td class='num'>{r['avg_age']:.0f}</td><td class='num'>{r['pct_female']:.0f}%</td></tr>"
            for _, r in df.head(5).iterrows())

    f_to = gen.set_index("gender").loc["F", "turnout_pct"]
    m_to = gen.set_index("gender").loc["M", "turnout_pct"]

    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>April 21, 2026 Referendum — Voter Analysis</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ font-family: 'Segoe UI', Helvetica, Arial, sans-serif; color:{INK}; margin:0; background:#eef2f7; }}
  .page {{ max-width: 980px; margin: 0 auto; background:#fff; padding: 26px 34px; }}
  h1 {{ font-size: 23px; margin: 0; }}
  .sub {{ color:#5a6b7b; font-size: 13px; margin: 2px 0 16px; }}
  .cards {{ display:flex; gap:12px; margin-bottom:16px; }}
  .card {{ flex:1; background:{BLUE}; color:#fff; border-radius:10px; padding:12px 14px; }}
  .card.alt {{ background:#143a64; }}
  .card .big {{ font-size:26px; font-weight:800; line-height:1; }}
  .card .lbl {{ font-size:11px; opacity:.9; margin-top:5px; }}
  .resultbar {{ margin: 4px 0 18px; }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:18px 26px; }}
  .panel h3 {{ font-size:13px; margin:0 0 4px; color:{INK}; }}
  .panel .cap {{ font-size:11px; color:#6b7a8a; margin:0 0 6px; }}
  .findings {{ background:#f5f8fc; border-left:4px solid {BLUE}; padding:12px 16px; border-radius:6px; margin-top:6px; font-size:12.5px; break-inside:avoid; page-break-inside:avoid; }}
  .panel, .twocol {{ break-inside:avoid; page-break-inside:avoid; }}
  .findings li {{ margin-bottom:6px; }}
  table {{ width:100%; border-collapse:collapse; font-size:11.5px; }}
  th,td {{ text-align:left; padding:3px 6px; border-bottom:1px solid {GRID}; }}
  td.num, th.num {{ text-align:right; }}
  .twocol {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-top:14px; }}
  .foot {{ margin-top:18px; font-size:10.5px; color:#7b8794; border-top:1px solid {GRID}; padding-top:8px; }}
  @page {{ size: letter; margin: 0; }}
  /* print-only: scale the whole layout to fit a single US Letter page */
  @media print {{ body {{ background:#fff; }} .page {{ padding: 8mm 12mm; max-width:none; zoom: 0.70; }} }}
</style></head><body><div class="page">

<h1>Virginia Constitutional Amendment Referendum — April 21, 2026</h1>
<div class="sub">Voter analysis from the SBE "List of Those Who Voted" ({s['total']:,} ballots) · DPVA · generated 2026-05-21</div>

<div class="cards">
  <div class="card"><div class="big">{s['yes_pct']}%</div><div class="lbl">voted YES — amendment <b>PASSED</b></div></div>
  <div class="card alt"><div class="big">{s['turnout_pct']}%</div><div class="lbl">turnout of {s['reg_active']/1e6:.2f}M active registered</div></div>
  <div class="card"><div class="big">{s['total']/1e6:.2f}M</div><div class="lbl">votes cast on the question</div></div>
  <div class="card alt"><div class="big">76%</div><div class="lbl">voted in 3-or-4 of last 4 generals</div></div>
</div>

<div class="resultbar">{svg_result(s['yes_pct'], s['no_pct'])}</div>

<div class="grid">
  <div class="panel"><h3>Turnout by age vs 2025 General</h3><p class="cap">% of active registered voting, by age band</p>{chart_age}</div>
  <div class="panel"><h3>How people voted</h3><p class="cap">share of all {s['total']/1e6:.1f}M voters by method</p>{chart_method}</div>
  <div class="panel"><h3>Turnout by party</h3><p class="cap">% turnout (Van party ID + Dem-support score, dashboard method)</p>{chart_party}</div>
  <div class="panel"><h3>Voter consistency</h3><p class="cap">% of voters by # of last 4 Nov generals voted</p>{chart_vh}</div>
</div>

<div class="twocol">
  <div>
    <h3 style="font-size:13px;margin:0 0 4px;">Strongest YES localities</h3>
    <table><tr><th>Locality</th><th class="num">Yes</th><th class="num">Avg age</th><th class="num">% F</th></tr>{loc_rows(strong)}</table>
  </div>
  <div>
    <h3 style="font-size:13px;margin:0 0 4px;">Strongest NO localities</h3>
    <table><tr><th>Locality</th><th class="num">Yes</th><th class="num">Avg age</th><th class="num">% F</th></tr>{loc_rows(weak)}</table>
  </div>
</div>

<div class="findings"><b>Key findings</b>
<ul>
  <li><b>A base-mobilization electorate, not a new one.</b> 76% of voters had voted in 3-or-4 of the last 4 November generals; first-time voters were just 2.1%.</li>
  <li><b>Republicans turned out harder, Democrats' larger base carried it.</b> Rep turnout {pbars_val[1]:.0f}% vs Dem {pbars_val[0]:.0f}%, but Dem-leaning registrants outnumber Republicans ~{dem_reg:.1f}M to {rep_reg:.1f}M and were the majority of voters ({dem_share}% vs {rep_share}%). Geography was sharply partisan — strongest Yes in cities/NoVa, strongest No in southwest Virginia.</li>
  <li><b>Turnout climbed steeply with age</b> ({ref[0]:.0f}% at 18–24 to {max(ref):.0f}% at 65–74); women turned out {f_to-m_to:.1f} pp higher than men ({f_to:.1f}% vs {m_to:.1f}%).</li>
  <li><b>Method skewed old-early, young-day:</b> {m['Polls']/sum(m.values())*100:.0f}% election day, {m['AB_Inperson']/sum(m.values())*100:.0f}% in-person early, {m['AB_Mail']/sum(m.values())*100:.0f}% mail.</li>
</ul></div>

<div class="foot">Sources: Virginia SBE List of Those Who Voted (LTV2026_Ref, {s['total']:,} ballots on question), SBE official results &amp; turnout files, DPVA ENR app, and VAN voter file (party / vote history). Import reconciles to within 0.23% of SBE ballots cast. Covington City and Sussex County are under-reported in the source LTV file and excluded from locality rankings. Full detail: <code>analysis/LTV2026_Ref_Analysis.md</code>.</div>

</div></body></html>"""
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({len(html)/1024:.1f} KB)")


if __name__ == "__main__":
    main()
