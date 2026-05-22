"""
make_churn_brief.py
-------------------
One-page visual brief on VOTER CHURN between the 2025 General and the April 2026
referendum: drop-off (2025G voters who didn't return) and surge (referendum
voters who skipped 2025G). Self-contained HTML (inline SVG); print to one page.

Reads:  analysis\\LTV2026_Ref_Analysis.xlsx (sheets 5i_* and 5j_*)
Writes: analysis\\Referendum2026_Churn_Brief.html
Aggregate only — no PII.
"""
from pathlib import Path
import pandas as pd
from make_publication import (svg_bars, svg_grouped, esc, INK, BLUE, LBLUE, DEM, REP,
                              NAV_CSS, nav_html, BRAND_CSS, brand_bar)

PROJ = Path(r"C:\DPVA_Projects\Referendum2026")
XLSX = PROJ / "analysis" / "LTV2026_Ref_Analysis.xlsx"
OUT = PROJ / "analysis" / "Referendum2026_Churn_Brief.html"
RED = "#c05a6e"      # drop-off (loss)
GRN = "#2f8f5b"      # surge (gain)
BAND = ['18-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75+']


def shorten(name):
    return (name.replace(" (City)", "").replace(" County", "")
            .replace("Prince William", "Pr. William")
            .replace("Virginia Beach", "Va Beach"))


def main():
    dpar = pd.read_excel(XLSX, "5i_dropoff_party")
    dcc = pd.read_excel(XLSX, "5i_dropoff_county_count")
    spar = pd.read_excel(XLSX, "5j_surge_party")
    dap = pd.read_excel(XLSX, "5i_dropoff_age_party")
    sap = pd.read_excel(XLSX, "5j_surge_age_party")

    g25_total = int(dpar.g25_voters.sum())
    drop_total = int(dpar.dropped_off.sum())
    ref_in_van = int(spar.ref_voters.sum())
    surge_total = int(spar.surge.sum())
    retention = (g25_total - drop_total) / g25_total * 100
    net = surge_total - drop_total
    dp = dpar.set_index("party_bucket")
    sp = spar.set_index("party_bucket")

    # grouped Dem-vs-Rep series by age band
    def grp(df):
        p = df.pivot(index="age_band", columns="party_bucket", values="rate").reindex(BAND)
        return ([round(float(x), 1) for x in p["Dem"]], [round(float(x), 1) for x in p["Rep"]])
    dd, dr = grp(dap)
    sd, sr = grp(sap)
    c_dgrp = svg_grouped(BAND, dd, dr, "Dem", "Rep", w=470, h=215, ymax=50, c1=DEM, c2=REP, gstep=10)
    c_sgrp = svg_grouped(BAND, sd, sr, "Dem", "Rep", w=470, h=215, ymax=30, c1=DEM, c2=REP, gstep=10)
    top = dcc.head(8)
    c_dloc = svg_bars([shorten(n) for n in top.locality], [round(int(x) / 1000) for x in top.dropped_off],
                      RED, w=920, h=180, ymax=max(top.dropped_off) / 1000 * 1.25, suffix="k")

    dem_d = round(float(dp.loc["Dem", "dropoff_pct"]))
    rep_d = round(float(dp.loc["Rep", "dropoff_pct"]))
    dem_s = round(float(sp.loc["Dem", "surge_pct"]), 1)
    rep_s = round(float(sp.loc["Rep", "surge_pct"]), 1)
    yd_dem, yd_rep = dd[0], dr[0]   # 18-24 drop-off Dem / Rep

    html = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Referendum 2026 — Voter Churn (Drop-off & Surge)</title>
<style>
  * {{ box-sizing:border-box; }}
  body {{ font-family:'Segoe UI',Helvetica,Arial,sans-serif; color:{INK}; margin:0; background:#eef2f7; }}
  .page {{ max-width:980px; margin:0 auto; background:#fff; padding:26px 34px; }}
  h1 {{ font-size:22px; margin:0; }}
  .sub {{ color:#5a6b7b; font-size:13px; margin:2px 0 16px; }}
  .cards {{ display:flex; gap:12px; margin-bottom:16px; }}
  .card {{ flex:1; color:#fff; border-radius:10px; padding:12px 14px; }}
  .card .big {{ font-size:25px; font-weight:800; line-height:1; }}
  .card .lbl {{ font-size:11px; opacity:.92; margin-top:5px; }}
  .loss {{ background:{RED}; }} .gain {{ background:{GRN}; }} .neutral {{ background:#143a64; }} .net {{ background:#5a6b7b; }}
  h2 {{ font-size:14px; margin:14px 0 2px; }}
  .colhead {{ font-size:12px; color:#5a6b7b; margin:0 0 8px; }}
  .grid {{ display:grid; grid-template-columns:1fr 1fr; gap:14px 26px; }}
  .panel h3 {{ font-size:12.5px; margin:0 0 2px; }} .panel .cap {{ font-size:10.5px; color:#6b7a8a; margin:0 0 4px; }}
  .panel, .findings {{ break-inside:avoid; page-break-inside:avoid; }}
  .findings {{ background:#f5f8fc; border-left:4px solid {BLUE}; padding:12px 16px; border-radius:6px; margin-top:14px; font-size:12.5px; }}
  .findings li {{ margin-bottom:5px; }}
  .foot {{ margin-top:16px; font-size:10.5px; color:#7b8794; border-top:1px solid #dde3ea; padding-top:8px; }}
  @page {{ size:letter; margin:0; }}
  @media print {{ body {{ background:#fff; }} .page {{ padding:9mm 12mm; max-width:none; zoom:0.82; }} }}
  {NAV_CSS}
  {BRAND_CSS}
</style></head><body><div class="page">
{brand_bar()}
{nav_html('churn')}
<h1>Referendum 2026 — Voter Churn: Drop-off &amp; Surge</h1>
<div class="sub">Who left and who arrived between the 2025 General and the April 21, 2026 referendum · DPVA · 2026-05-21</div>

<div class="cards">
  <div class="card neutral"><div class="big">{retention:.0f}%</div><div class="lbl">of 2025 General voters returned ({g25_total:,} total)</div></div>
  <div class="card loss"><div class="big">{drop_total:,}</div><div class="lbl">dropped off — voted 2025G, skipped referendum ({drop_total/g25_total*100:.0f}%)</div></div>
  <div class="card gain"><div class="big">{surge_total:,}</div><div class="lbl">surged in — voted referendum, skipped 2025G ({surge_total/ref_in_van*100:.0f}%)</div></div>
  <div class="card net"><div class="big">{net:+,}</div><div class="lbl">net change vs 2025G (VAN-matched)</div></div>
</div>

<div class="grid">
  <div class="panel"><h3 style="color:{RED}">Drop-off rate by age &amp; party</h3><p class="cap">% of each band's 2025G voters who skipped the referendum — Dem vs Rep</p>{c_dgrp}</div>
  <div class="panel"><h3 style="color:{GRN}">Surge rate by age &amp; party</h3><p class="cap">% of each band's referendum voters who skipped 2025G — Dem vs Rep</p>{c_sgrp}</div>
</div>
<div class="panel" style="margin-top:10px"><h3 style="color:{RED}">Where the lost voters are — top localities by drop-off count</h3><p class="cap">thousands of 2025G voters who didn't return</p>{c_dloc}</div>

<div class="findings"><b>What it means</b>
<ul>
  <li><b>Drop-off skews young and Democratic — at every age.</b> Democrats dropped off more than Republicans in every band (overall {dem_d}% vs {rep_d}%), widest among the young: {yd_dem:.0f}% of Dem 18–24s vs {yd_rep:.0f}% of Rep. The Yes win came <i>despite</i> losing more of the Dem base — cushioned by its size.</li>
  <li><b>Surge skews young but slightly Republican.</b> New-to-2025G referendum voters were {rep_s}% of Rep voters vs {dem_s}% of Dems — Democrats lost more of their base <i>and</i> replaced less of it.</li>
  <li><b>Re-mobilization target:</b> young, Dem-leaning 2025 voters — highest volume in Fairfax / Loudoun / Prince William, highest rate in college towns (Harrisonburg, Charlottesville, Williamsburg). Voter-level list available (held privately, VAN-ready).</li>
</ul></div>

<div class="foot"><b>Eligibility note:</b> the youngest surge band is modestly inflated by ~5,400 voters who turned 18 after the 2025 General (eligible for the referendum, not 2025G) — only 1.6% of all surge. Excluding them, the 18–24 surge rate is <b>22.8%</b> rather than 24.9%, so the young tilt is overwhelmingly genuine. &nbsp;Source: 2025-General vote history and 2026 referendum participation matched in the VAN voter file (Van party ID + Dem-support score). "Drop-off" and "surge" are limited to voters present in VAN; ~25k referendum voters with no VAN record (new registrations) are additional surge. Aggregate counts only — no individual voter data. Detail: <code>analysis/LTV2026_Ref_Analysis.md</code> §5i–5j.</div>

</div></body></html>"""
    OUT.write_text(html, encoding="utf-8")
    print(f"Wrote {OUT} ({len(html)/1024:.1f} KB)")


if __name__ == "__main__":
    main()
