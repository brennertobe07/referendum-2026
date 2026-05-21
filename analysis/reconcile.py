"""
reconcile.py  (Phase 4)
-----------------------
Validate the LTV2026_Ref import against three external sources and write
analysis\\reconciliation.md.

  Source A - SBE official results + turnout files (votes on question / ballots).
  Source B - Our ENR app data (localities.json) - locality-by-locality.
  Source C - Absentee app data (Absentee.dbo.Daily_Absentee_List).
"""

import json
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

PROJ = Path(r"C:\DPVA_Projects\Referendum2026")
ENR = Path(r"C:\Scripts\Python\Python_ElectionResults\april-referendum-enr\data")
RESULTS = Path(r"C:\Temp\SBE\Results_Winners\NewFormat\Election Results2026_Ref.csv")
TURNOUT = Path(r"C:\Temp\SBE\Results_Winners\NewFormat\Election Turnout_2026_Ref.csv")
ELECTION = "2026 April 21 Special"


def eng(db):
    return create_engine(
        f"mssql+pyodbc://INSTANCE-1/{db}"
        "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    )


def main():
    hist = eng("Historic")
    absn = eng("Absentee")

    # ---- LTV aggregates ----
    ltv_total = int(pd.read_sql("SELECT COUNT(*) n FROM dbo.LTV2026_Ref", hist).n[0])
    ltv_distinct = int(pd.read_sql(
        "SELECT COUNT(DISTINCT IDENTIFICATION_NUMBER) n FROM dbo.LTV2026_Ref", hist).n[0])
    ltv_abs = pd.read_sql(
        "SELECT ABSENTEE, COUNT(*) c FROM dbo.LTV2026_Ref GROUP BY ABSENTEE", hist)
    ltv_true = int(ltv_abs.loc[ltv_abs.ABSENTEE == "True", "c"].sum())
    ltv_false = int(ltv_abs.loc[ltv_abs.ABSENTEE == "False", "c"].sum())
    ltv_loc = pd.read_sql(
        "SELECT LOCALITY_CODE, MAX(LOCALITYNAME) AS LOCALITYNAME, COUNT(*) AS ltv_voters "
        "FROM dbo.LTV2026_Ref GROUP BY LOCALITY_CODE", hist)
    vm = pd.read_sql(
        "SELECT AB_Type, COUNT(*) c FROM dbo.LTV2026_Ref_Votemethod GROUP BY AB_Type", hist)
    vm_d = dict(zip(vm.AB_Type, vm.c))

    # ---- Source C: DAL accepted absentee ----
    dal_rows = int(pd.read_sql(
        "SELECT COUNT(*) n FROM dbo.Daily_Absentee_List "
        f"WHERE ELECTION_NAME='{ELECTION}' "
        "AND BALLOT_STATUS IN ('On Machine','Marked','Pre-Processed')", absn).n[0])
    dal_voters = int(pd.read_sql(
        "SELECT COUNT(*) n FROM (SELECT IDENTIFICATION_NUMBER FROM dbo.Daily_Absentee_List "
        f"WHERE ELECTION_NAME='{ELECTION}' "
        "AND BALLOT_STATUS IN ('On Machine','Marked','Pre-Processed') "
        "GROUP BY IDENTIFICATION_NUMBER) x", absn).n[0])

    # ---- Source A: SBE results + turnout ----
    res = pd.read_csv(RESULTS, dtype=str)
    res["v"] = pd.to_numeric(res["TOTAL_VOTES"], errors="coerce").fillna(0)
    sbe_yes = int(res.loc[res.CandidateName == "Yes", "v"].sum())
    sbe_no = int(res.loc[res.CandidateName == "No", "v"].sum())
    sbe_votes = sbe_yes + sbe_no
    res_loc = res.groupby("LocalityCode")["v"].sum().rename("sbe_votes").reset_index()

    tn = pd.read_csv(TURNOUT, dtype=str)
    mcols = ["Early Voting", "Election Day", "Mailed Absentee", "Provisional",
             "Post-Election", "TotalVoteTurnout", "ActiveRegisteredVoters"]
    for c in mcols:
        tn[c] = pd.to_numeric(tn[c], errors="coerce").fillna(0)
    turnout_ballots = int(tn["TotalVoteTurnout"].sum())
    method = {c: int(tn[c].sum()) for c in
              ["Early Voting", "Election Day", "Mailed Absentee", "Provisional", "Post-Election"]}
    active_reg = int(tn["ActiveRegisteredVoters"].sum())

    # ---- Source B: ENR localities.json ----
    enr = pd.DataFrame(json.load(open(ENR / "localities.json")))
    enr["fips"] = enr["fips"].astype(str).str.zfill(3)
    summ = json.load(open(ENR / "summary.json"))

    # locality reconciliation: LTV voters vs ENR total (votes on question)
    ltv_loc = ltv_loc.copy()
    ltv_loc["LOCALITY_CODE"] = ltv_loc["LOCALITY_CODE"].astype(str).str.zfill(3)
    recon = ltv_loc.merge(
        enr[["fips", "name", "total"]].rename(
            columns={"fips": "LOCALITY_CODE", "total": "enr_ballots", "name": "enr_name"}),
        on="LOCALITY_CODE", how="outer")
    recon["ltv_voters"] = recon["ltv_voters"].fillna(0).astype(int)
    recon["enr_ballots"] = recon["enr_ballots"].fillna(0).astype(int)
    recon["Locality"] = recon["LOCALITYNAME"].fillna(recon["enr_name"])
    recon["Delta"] = recon["ltv_voters"] - recon["enr_ballots"]
    recon["pct"] = (recon["Delta"].abs() /
                    recon["ltv_voters"].replace(0, pd.NA) * 100)
    recon = recon.sort_values("LOCALITY_CODE")
    flagged = recon[recon["pct"] > 1.0].copy()

    # ---- write reconciliation.md ----
    L = []
    L.append("# Referendum 2026 — Import Reconciliation (Phase 4)\n")
    L.append(f"_Generated 2026-05-21. Election: {ELECTION}._\n")
    L.append("## Headline result (SBE / ENR certified)\n")
    L.append(f"- **Yes {summ['yes']:,} ({summ['yes_pct']}%)** vs No {summ['no']:,} "
             f"({summ['no_pct']}%) — amendment **{'PASSED' if summ['yes_pct']>50 else 'FAILED'}**.")
    L.append(f"- Votes on question: {summ['total']:,}. Precincts reporting: "
             f"{summ['pct_reporting']}%.")
    L.append(f"- Turnout: **{summ['turnout_pct']}%** of {summ['reg_active']:,} active "
             f"registered ({summ['reg_all']:,} total registered).\n")

    L.append("## Source A — SBE official results & turnout file\n")
    L.append("| Metric | Count |")
    L.append("|---|---|")
    L.append(f"| LTV2026_Ref rows (voters) | {ltv_total:,} |")
    L.append(f"| LTV distinct IDENTIFICATION_NUMBER | {ltv_distinct:,} |")
    L.append(f"| SBE votes on question (Yes {sbe_yes:,} + No {sbe_no:,}) | {sbe_votes:,} |")
    L.append(f"| SBE total ballots cast (turnout file TotalVoteTurnout) | {turnout_ballots:,} |")
    L.append(f"| Delta: LTV voters − SBE ballots cast | {ltv_total - turnout_ballots:+,} |")
    L.append(f"| Delta: LTV voters − SBE votes on question | {ltv_total - sbe_votes:+,} |")
    d_ballots = (ltv_total - turnout_ballots) / turnout_ballots * 100
    L.append(f"\nLTV voters are within **{d_ballots:+.3f}%** of SBE ballots cast. "
             "Expected sign: ballots cast ≥ voters in LTV ≈ votes on question "
             "(undervotes make votes-on-question < ballots).\n")

    L.append("## Source A — vote-method cross-check (SBE turnout vs LTV derivation)\n")
    L.append("| Method | SBE turnout file | LTV2026_Ref_Votemethod | Note |")
    L.append("|---|---|---|---|")
    L.append(f"| Election Day | {method['Election Day']:,} | {vm_d.get('Polls',0):,} | LTV 'Polls' |")
    L.append(f"| Early Voting (in-person) | {method['Early Voting']:,} | {vm_d.get('AB_Inperson',0):,} | LTV 'AB_Inperson' |")
    L.append(f"| Mailed Absentee | {method['Mailed Absentee']:,} | {vm_d.get('AB_Mail',0):,} | LTV 'AB_Mail' |")
    L.append(f"| Provisional + Post-Election | {method['Provisional']+method['Post-Election']:,} | {vm_d.get('AB_Other',0):,} | LTV 'AB_Other' (approx) |")
    L.append("")

    L.append("## Source B — ENR app locality reconciliation\n")
    L.append("LTV voters per locality vs ENR app `total` (votes on question). "
             f"Localities flagged where |Delta| > 1% of LTV voters: **{len(flagged)}**.\n")
    if len(flagged):
        L.append("| Locality | LTV_Voters | ENR_Ballots | Delta | Δ% |")
        L.append("|---|---|---|---|---|")
        for _, r in flagged.sort_values("pct", ascending=False).iterrows():
            L.append(f"| {r['Locality']} | {r['ltv_voters']:,} | {r['enr_ballots']:,} "
                     f"| {r['Delta']:+,} | {r['pct']:.2f}% |")
    else:
        L.append("_No localities exceeded the 1% threshold._")
    L.append(f"\nStatewide: LTV {recon['ltv_voters'].sum():,} voters vs ENR "
             f"{recon['enr_ballots'].sum():,} votes-on-question "
             f"(Δ {recon['ltv_voters'].sum()-recon['enr_ballots'].sum():+,}). "
             f"Localities matched: {recon['LOCALITY_CODE'].nunique()}.\n")

    L.append("## Source C — Absentee app reconciliation\n")
    match = dal_rows / ltv_true * 100
    L.append("| Metric | Count |")
    L.append("|---|---|")
    L.append(f"| LTV absentee voters (ABSENTEE = True) | {ltv_true:,} |")
    L.append(f"| LTV election-day voters (ABSENTEE = False) | {ltv_false:,} |")
    L.append(f"| DAL accepted absentee ballots (On Machine + Marked + Pre-Processed) | {dal_rows:,} |")
    L.append(f"| DAL accepted absentee — distinct voters | {dal_voters:,} |")
    L.append(f"| ENR summary ab_voted | {summ['ab_voted']:,} |")
    L.append(f"| **Match rate (DAL accepted / LTV absentee)** | **{match:.2f}%** |")
    L.append("")

    out = PROJ / "analysis" / "reconciliation.md"
    out.write_text("\n".join(L), encoding="utf-8")
    print(f"Wrote {out}")
    print(f"LTV {ltv_total:,} | SBE ballots {turnout_ballots:,} | SBE votes {sbe_votes:,} "
          f"| ENR total {summ['total']:,}")
    print(f"Flagged localities (>1%): {len(flagged)}")
    print(f"Source C match: {match:.2f}%")
    recon.to_csv(PROJ / "analysis" / "locality_reconciliation.csv", index=False)


if __name__ == "__main__":
    main()
