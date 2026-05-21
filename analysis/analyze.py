"""
analyze.py  (Phase 5 + Phase 6 exec summary)
--------------------------------------------
Voter pattern analysis for the April 21, 2026 referendum.

Builds Historic.dbo.LTV2026_Ref_Base (LTV voters enriched with Van party/score +
vote history and an RVL-match flag), then runs sections 5a-5h and writes:
  analysis\\LTV2026_Ref_Analysis.md
  analysis\\LTV2026_Ref_Analysis.xlsx  (one sheet per analysis)

Denominators:
  - registered totals (turnout %): RVL where STATUS = 'Active'
  - party denominators: Voter.dbo.Van (RVL has no party)
  - baseline election: 2025 General (Van.General25) for age/gender turnout comparison
Join key: LTV.IDENTIFICATION_NUMBER = Van.StateFileID = RVL.IDENTIFICATION_NUMBER
"""

import json
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

PROJ = Path(r"C:\DPVA_Projects\Referendum2026")
ENR_LOC = Path(r"C:\Scripts\Python\Python_ElectionResults\april-referendum-enr\data\localities.json")
ELECTION_DAY = "2026-04-21"

AGE_BAND_SQL = """CASE
  WHEN age BETWEEN 18 AND 24 THEN '18-24'
  WHEN age BETWEEN 25 AND 34 THEN '25-34'
  WHEN age BETWEEN 35 AND 44 THEN '35-44'
  WHEN age BETWEEN 45 AND 54 THEN '45-54'
  WHEN age BETWEEN 55 AND 64 THEN '55-64'
  WHEN age BETWEEN 65 AND 74 THEN '65-74'
  WHEN age >= 75 THEN '75+'
  ELSE 'Unknown' END"""

BAND_ORDER = ['18-24', '25-34', '35-44', '45-54', '55-64', '65-74', '75+', 'Unknown']


def eng(db):
    return create_engine(
        f"mssql+pyodbc://INSTANCE-1/{db}"
        "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes",
        fast_executemany=True)


def age_expr(dob_col):
    return (f"DATEDIFF(YEAR, {dob_col}, '{ELECTION_DAY}') - "
            f"CASE WHEN MONTH({dob_col}) > 4 OR (MONTH({dob_col}) = 4 AND DAY({dob_col}) > 21) "
            f"THEN 1 ELSE 0 END")


def build_base(hist, voter):
    # full prior-vote history column set (any non-blank => has voted before 2026)
    hist_cols = pd.read_sql(text(
        "SELECT c.name FROM sys.columns c WHERE c.object_id=OBJECT_ID('Voter.dbo.Van') "
        "AND (c.name LIKE 'General%' OR c.name LIKE 'Municipal%' "
        "OR (c.name LIKE 'Primary%' AND c.name NOT LIKE '%Party') "
        "OR (c.name LIKE 'PresPrimary%' AND c.name NOT LIKE '%Party'))"), voter)["name"].tolist()
    prior = " + ".join(
        f"CASE WHEN NULLIF(LTRIM(RTRIM(v.[{c}])),'') IS NOT NULL THEN 1 ELSE 0 END"
        for c in hist_cols)
    gen4 = " + ".join(
        f"CASE WHEN NULLIF(LTRIM(RTRIM(v.[General{y}])),'') IS NOT NULL THEN 1 ELSE 0 END"
        for y in ['22', '23', '24', '25'])

    sql = f"""
    IF OBJECT_ID('Historic.dbo.LTV2026_Ref_Base','U') IS NOT NULL
        DROP TABLE Historic.dbo.LTV2026_Ref_Base;

    SELECT
        l.IDENTIFICATION_NUMBER,
        l.LOCALITY_CODE,
        l.LOCALITYNAME,
        l.PRECINCT_CODE_VALUE,
        l.PRECINCTNAME,
        UPPER(LTRIM(RTRIM(l.GENDER))) AS gender,
        TRY_CONVERT(date, l.DOB, 101) AS dob,
        TRY_CONVERT(date, l.REGISTRATION_DATE, 101) AS reg_date,
        l.ABSENTEE,
        vm.AB_Type,
        CASE WHEN v.StateFileID IS NULL THEN 0 ELSE 1 END AS in_van,
        CASE WHEN r.IDENTIFICATION_NUMBER IS NULL THEN 0 ELSE 1 END AS in_rvl,
        v.LikelyParty,
        CASE WHEN v.LikelyParty IN ('SD','LD') THEN 'Dem'
             WHEN v.LikelyParty IN ('SR','LR') THEN 'Rep'
             ELSE 'Unknown/Ind' END AS party_bucket,
        TRY_CONVERT(float, v.Clarity_DemSupport_26) AS dem_support,
        v.RaceName,
        ({gen4}) AS gen4,
        CASE WHEN ({prior}) > 0 THEN 1 ELSE 0 END AS prior_vote
    INTO Historic.dbo.LTV2026_Ref_Base
    FROM Historic.dbo.LTV2026_Ref l
    LEFT JOIN Historic.dbo.LTV2026_Ref_Votemethod vm
        ON vm.IDENTIFICATION_NUMBER = l.IDENTIFICATION_NUMBER
    LEFT JOIN Voter.dbo.Van v ON v.StateFileID = l.IDENTIFICATION_NUMBER
    LEFT JOIN Voter.dbo.RVL r ON r.IDENTIFICATION_NUMBER = l.IDENTIFICATION_NUMBER;
    """
    with hist.begin() as cx:
        cx.execute(text(sql))
        # add age + age_band as persisted columns for convenient querying
        cx.execute(text(f"ALTER TABLE Historic.dbo.LTV2026_Ref_Base ADD age AS ({age_expr('dob')});"))
    with hist.begin() as cx:
        cx.execute(text("CREATE INDEX IX_base_loc ON Historic.dbo.LTV2026_Ref_Base(LOCALITY_CODE);"))
    n = pd.read_sql(text("SELECT COUNT(*) n FROM Historic.dbo.LTV2026_Ref_Base"), hist)["n"][0]
    return int(n)


def q(engine, sql):
    return pd.read_sql(text(sql), engine)


def main():
    hist = eng("Historic")
    voter = eng("Voter")

    nbase = build_base(hist, voter)

    sheets = {}   # name -> DataFrame for xlsx
    md = []
    md.append("# Referendum 2026 — Voter Pattern Analysis (Phase 5)\n")
    md.append(f"_Generated 2026-05-21. Base table `Historic.dbo.LTV2026_Ref_Base` "
              f"= {nbase:,} LTV voters enriched with Van party/history + RVL match._\n")
    md.append("> **Caveats:** turnout denominators use RVL `STATUS='Active'`; party uses "
              "Van `LikelyParty` (SD/LD=Dem, SR/LR=Rep, ND/I/U=Unknown/Ind); baseline = 2025 "
              "General (Van `General25`). COVINGTON CITY (580) and SUSSEX COUNTY (183) are "
              "under-reported in the LTV source (~1/3 of actual) — locality-level rows for "
              "them are unreliable; statewide/demographic results are unaffected (<0.1%).\n")

    AB = "Historic.dbo.LTV2026_Ref_Base"

    # ---------- 5a First-time voters ----------
    ft = q(hist, f"""
        SELECT
          SUM(CASE WHEN in_van=1 AND prior_vote=0 THEN 1 ELSE 0 END) AS first_time_matched,
          SUM(CASE WHEN in_van=0 THEN 1 ELSE 0 END) AS no_van_record,
          SUM(CASE WHEN in_van=1 AND prior_vote=1 THEN 1 ELSE 0 END) AS returning,
          COUNT(*) AS total
        FROM {AB}""")
    ftm, novan, ret, tot = (int(ft.first_time_matched[0]), int(ft.no_van_record[0]),
                            int(ft.returning[0]), int(ft.total[0]))
    ft_broad = ftm + novan
    # registered base: % of active RVL that are "new" (registered after 2025-11-04 general)
    reg_new = q(voter, """
        SELECT
          SUM(CASE WHEN TRY_CONVERT(date,REGISTRATION_DATE,101) > '2025-11-04' THEN 1 ELSE 0 END) AS new_reg,
          SUM(CASE WHEN STATUS='Active' THEN 1 ELSE 0 END) AS active
        FROM Voter.dbo.RVL WHERE STATUS='Active'""")
    md.append("## 5a. First-time voters\n")
    md.append(f"- **First-time (broad): {ft_broad:,} ({ft_broad/tot*100:.1f}% of voters)** "
              f"= {ftm:,} matched in Van with no prior vote + {novan:,} with no Van record "
              f"(likely new registrations after the Van snapshot).")
    md.append(f"- Returning voters (≥1 prior election in Van): {ret:,} ({ret/tot*100:.1f}%).")
    md.append("")
    # breakdowns of first-time (broad) by age band, gender, party, top localities
    ftb_age = q(hist, f"""
        SELECT {AGE_BAND_SQL} AS age_band, COUNT(*) AS first_time
        FROM {AB} WHERE (in_van=1 AND prior_vote=0) OR in_van=0
        GROUP BY {AGE_BAND_SQL}""")
    ftb_age["age_band"] = pd.Categorical(ftb_age["age_band"], BAND_ORDER, ordered=True)
    ftb_age = ftb_age.sort_values("age_band")
    sheets["5a_firsttime_by_age"] = ftb_age
    ftb_party = q(hist, f"""
        SELECT party_bucket, COUNT(*) AS first_time
        FROM {AB} WHERE (in_van=1 AND prior_vote=0) OR in_van=0
        GROUP BY party_bucket ORDER BY first_time DESC""")
    sheets["5a_firsttime_by_party"] = ftb_party
    md.append("First-time voters by age band:\n")
    md.append(df_to_md(ftb_age))
    md.append("\nFirst-time voters by party bucket:\n")
    md.append(df_to_md(ftb_party))
    md.append(f"\n_Comparison: {int(reg_new.new_reg[0]):,} of {int(reg_new.active[0]):,} active "
              f"registered voters ({int(reg_new.new_reg[0])/int(reg_new.active[0])*100:.1f}%) "
              f"registered after the Nov 2025 general — the referendum's first-time share "
              f"({ft_broad/tot*100:.1f}%) {'exceeds' if ft_broad/tot*100 > int(reg_new.new_reg[0])/int(reg_new.active[0])*100 else 'is below'} "
              f"that baseline._\n")

    # ---------- 5b Age / generation ----------
    voted_age = q(hist, f"SELECT {AGE_BAND_SQL} AS age_band, COUNT(*) AS voted FROM {AB} GROUP BY {AGE_BAND_SQL}")
    reg_age = q(voter, f"""SELECT {AGE_BAND_SQL.replace('age', age_expr('TRY_CONVERT(date,DOB,101)'))} AS age_band,
                 COUNT(*) AS registered
                 FROM Voter.dbo.RVL WHERE STATUS='Active'
                 GROUP BY {AGE_BAND_SQL.replace('age', age_expr('TRY_CONVERT(date,DOB,101)'))}""")
    base_age = q(voter, f"""SELECT {AGE_BAND_SQL.replace('age','Age')} AS age_band,
                 SUM(CASE WHEN NULLIF(LTRIM(RTRIM(General25)),'') IS NOT NULL THEN 1 ELSE 0 END) AS voted25,
                 COUNT(*) AS reg25
                 FROM Voter.dbo.Van GROUP BY {AGE_BAND_SQL.replace('age','Age')}""")
    age = voted_age.merge(reg_age, on="age_band", how="outer").merge(base_age, on="age_band", how="outer")
    age["age_band"] = pd.Categorical(age["age_band"], BAND_ORDER, ordered=True)
    age = age.sort_values("age_band")
    age["turnout_pct"] = (age["voted"] / age["registered"] * 100).round(1)
    age["baseline_2025G_pct"] = (age["voted25"] / age["reg25"] * 100).round(1)
    age["vs_baseline_pp"] = (age["turnout_pct"] - age["baseline_2025G_pct"]).round(1)
    age = age[["age_band", "voted", "registered", "turnout_pct", "baseline_2025G_pct", "vs_baseline_pp"]]
    sheets["5b_age"] = age
    md.append("## 5b. Age and generation\n")
    md.append("Turnout % = LTV voters / RVL active registered, by age (as of 2026-04-21). "
              "Baseline = 2025 General turnout in Van.\n")
    md.append(df_to_md(age))
    md.append("")

    # ---------- 5c Gender ----------
    voted_g = q(hist, f"SELECT gender, COUNT(*) AS voted FROM {AB} WHERE gender IN ('M','F') GROUP BY gender")
    reg_g = q(voter, "SELECT UPPER(LTRIM(RTRIM(GENDER))) AS gender, COUNT(*) AS registered FROM Voter.dbo.RVL WHERE STATUS='Active' AND UPPER(LTRIM(RTRIM(GENDER))) IN ('M','F') GROUP BY UPPER(LTRIM(RTRIM(GENDER)))")
    base_g = q(voter, "SELECT UPPER(Sex) AS gender, SUM(CASE WHEN NULLIF(LTRIM(RTRIM(General25)),'') IS NOT NULL THEN 1 ELSE 0 END) AS voted25, COUNT(*) AS reg25 FROM Voter.dbo.Van WHERE UPPER(Sex) IN ('M','F') GROUP BY UPPER(Sex)")
    gen = voted_g.merge(reg_g, on="gender").merge(base_g, on="gender")
    gen["turnout_pct"] = (gen["voted"] / gen["registered"] * 100).round(1)
    gen["baseline_2025G_pct"] = (gen["voted25"] / gen["reg25"] * 100).round(1)
    gen["vs_baseline_pp"] = (gen["turnout_pct"] - gen["baseline_2025G_pct"]).round(1)
    gen = gen[["gender", "voted", "registered", "turnout_pct", "baseline_2025G_pct", "vs_baseline_pp"]]
    sheets["5c_gender"] = gen
    md.append("## 5c. Gender\n")
    md.append(df_to_md(gen))
    md.append("")

    # ---------- 5d Vote history pattern (last 4 generals) ----------
    vh = q(hist, f"SELECT gen4 AS generals_voted_of_4, COUNT(*) AS voters FROM {AB} WHERE in_van=1 GROUP BY gen4 ORDER BY gen4")
    vh["pct"] = (vh["voters"] / vh["voters"].sum() * 100).round(1)
    sheets["5d_votehistory"] = vh
    high = int(vh[vh.generals_voted_of_4 >= 3]["voters"].sum())
    low = int(vh[vh.generals_voted_of_4 <= 1]["voters"].sum())
    md.append("## 5d. Vote history pattern (last 4 Nov generals: 2022-2025)\n")
    md.append("Among LTV voters matched in Van:\n")
    md.append(df_to_md(vh))
    story = "base mobilization" if high > low else "new electorate"
    md.append(f"\n**3-of-4 or 4-of-4: {high:,} ({high/int(vh.voters.sum())*100:.1f}%)** vs "
              f"**0-of-4 or 1-of-4: {low:,} ({low/int(vh.voters.sum())*100:.1f}%)**. "
              f"This referendum is a **{story}** story.\n")

    # ---------- 5e Vote method ----------
    vm_age = q(hist, f"SELECT {AGE_BAND_SQL} AS age_band, AB_Type, COUNT(*) AS voters FROM {AB} GROUP BY {AGE_BAND_SQL}, AB_Type")
    vm_age_p = vm_age.pivot_table(index="age_band", columns="AB_Type", values="voters", fill_value=0).reset_index()
    vm_age_p["age_band"] = pd.Categorical(vm_age_p["age_band"], BAND_ORDER, ordered=True)
    vm_age_p = vm_age_p.sort_values("age_band")
    sheets["5e_method_by_age"] = vm_age_p
    vm_party = q(hist, f"SELECT party_bucket, AB_Type, COUNT(*) AS voters FROM {AB} GROUP BY party_bucket, AB_Type")
    vm_party_p = vm_party.pivot_table(index="party_bucket", columns="AB_Type", values="voters", fill_value=0).reset_index()
    sheets["5e_method_by_party"] = vm_party_p
    md.append("## 5e. Vote method (Election day=Polls, In-person early=AB_Inperson, Mail=AB_Mail)\n")
    md.append("By age band (voter counts):\n")
    md.append(df_to_md(vm_age_p))
    # mail share by age
    mc = vm_age_p.copy()
    typecols = [c for c in mc.columns if c != "age_band"]
    mc["mail_pct"] = (mc.get("AB_Mail", 0) / mc[typecols].sum(axis=1) * 100).round(1)
    md.append("\nBy party bucket:\n")
    md.append(df_to_md(vm_party_p))
    md.append("")

    # ---------- 5f Geography ----------
    loc_cnt = q(hist, f"""SELECT TOP 10 LOCALITY_CODE, MAX(LOCALITYNAME) AS locality, COUNT(*) AS ltv_voters
        FROM {AB} GROUP BY LOCALITY_CODE ORDER BY COUNT(*) DESC""")
    sheets["5f_top10_count"] = loc_cnt
    loc_to = q(hist, f"""
        WITH v AS (SELECT LOCALITY_CODE, MAX(LOCALITYNAME) loc, COUNT(*) voted FROM {AB} GROUP BY LOCALITY_CODE),
             r AS (SELECT LOCALITY_CODE, COUNT(*) reg FROM Voter.dbo.RVL WHERE STATUS='Active' GROUP BY LOCALITY_CODE)
        SELECT TOP 10 v.LOCALITY_CODE, v.loc AS locality, v.voted, r.reg,
               CAST(100.0*v.voted/NULLIF(r.reg,0) AS DECIMAL(5,1)) AS turnout_pct
        FROM v JOIN r ON r.LOCALITY_CODE=v.LOCALITY_CODE
        WHERE v.LOCALITY_CODE NOT IN ('580','183')
        ORDER BY turnout_pct DESC""")
    sheets["5f_top10_turnout"] = loc_to
    md.append("## 5f. Geography\n")
    md.append("Top 10 localities by LTV voter count:\n")
    md.append(df_to_md(loc_cnt[["locality", "ltv_voters"]]))
    md.append("\nTop 10 localities by turnout % (LTV voters / RVL active; Covington/Sussex excluded):\n")
    md.append(df_to_md(loc_to[["locality", "voted", "reg", "turnout_pct"]]))

    # Yes% strongest vs weakest, joined to demographic profile
    enr = pd.DataFrame(json.load(open(ENR_LOC)))
    enr["fips"] = enr["fips"].astype(str).str.zfill(3)
    prof = q(hist, f"""SELECT LOCALITY_CODE,
               AVG(CAST(age AS FLOAT)) AS avg_age,
               100.0*SUM(CASE WHEN gender='F' THEN 1 ELSE 0 END)/COUNT(*) AS pct_female,
               100.0*SUM(CASE WHEN (in_van=1 AND prior_vote=0) OR in_van=0 THEN 1 ELSE 0 END)/COUNT(*) AS pct_firsttime
               FROM {AB} GROUP BY LOCALITY_CODE""")
    enr2 = enr.merge(prof, left_on="fips", right_on="LOCALITY_CODE", how="left")
    enr2 = enr2[~enr2["fips"].isin(["580", "183"])]
    strong = enr2.sort_values("yes_pct", ascending=False).head(10)[["name", "yes_pct", "avg_age", "pct_female", "pct_firsttime"]]
    weak = enr2.sort_values("yes_pct").head(10)[["name", "yes_pct", "avg_age", "pct_female", "pct_firsttime"]]
    for d in (strong, weak):
        for c in ("avg_age", "pct_female", "pct_firsttime"):
            d[c] = d[c].round(1)
    sheets["5f_strong_yes"] = strong
    sheets["5f_weak_yes"] = weak
    md.append("\nStrongest YES localities — voter profile:\n")
    md.append(df_to_md(strong))
    md.append("\nStrongest NO localities — voter profile:\n")
    md.append(df_to_md(weak))
    md.append("")

    # ---------- 5g Party ----------
    pv = q(hist, f"SELECT party_bucket, COUNT(*) AS voted FROM {AB} GROUP BY party_bucket")
    pr = q(voter, """SELECT CASE WHEN LikelyParty IN ('SD','LD') THEN 'Dem'
                              WHEN LikelyParty IN ('SR','LR') THEN 'Rep' ELSE 'Unknown/Ind' END AS party_bucket,
                       COUNT(*) AS registered FROM Voter.dbo.Van GROUP BY
                       CASE WHEN LikelyParty IN ('SD','LD') THEN 'Dem'
                            WHEN LikelyParty IN ('SR','LR') THEN 'Rep' ELSE 'Unknown/Ind' END""")
    party = pv.merge(pr, on="party_bucket", how="left")
    party["turnout_pct"] = (party["voted"] / party["registered"] * 100).round(1)
    party["share_of_voters_pct"] = (party["voted"] / party["voted"].sum() * 100).round(1)
    sheets["5g_party"] = party
    md.append("## 5g. Party (from Van LikelyParty; denominator = Van registered)\n")
    md.append(df_to_md(party))
    dem_to = party.loc[party.party_bucket == "Dem", "turnout_pct"].values
    rep_to = party.loc[party.party_bucket == "Rep", "turnout_pct"].values
    if len(dem_to) and len(rep_to):
        md.append(f"\nDem turnout {dem_to[0]}% vs Rep turnout {rep_to[0]}% — "
                  f"skew of {abs(dem_to[0]-rep_to[0]):.1f} pp toward "
                  f"{'Dem' if dem_to[0] > rep_to[0] else 'Rep'}.\n")

    # ---------- 5h Anomaly scan ----------
    # precinct turnout vs statewide mean +/- 2 SD
    prec = q(hist, f"""
        WITH v AS (SELECT LOCALITY_CODE, PRECINCT_CODE_VALUE, MAX(LOCALITYNAME) loc, MAX(PRECINCTNAME) prec, COUNT(*) voted
                   FROM {AB} GROUP BY LOCALITY_CODE, PRECINCT_CODE_VALUE),
             r AS (SELECT LOCALITY_CODE, PRECINCT_CODE_VALUE, COUNT(*) reg
                   FROM Voter.dbo.RVL WHERE STATUS='Active' GROUP BY LOCALITY_CODE, PRECINCT_CODE_VALUE)
        SELECT v.loc AS locality, v.prec AS precinct, v.voted, r.reg,
               100.0*v.voted/NULLIF(r.reg,0) AS turnout_pct
        FROM v JOIN r ON r.LOCALITY_CODE=v.LOCALITY_CODE AND r.PRECINCT_CODE_VALUE=v.PRECINCT_CODE_VALUE
        WHERE r.reg >= 100 AND v.LOCALITY_CODE NOT IN ('580','183')""")
    mean, sd = prec["turnout_pct"].mean(), prec["turnout_pct"].std()
    prec["z"] = (prec["turnout_pct"] - mean) / sd
    anom = prec[prec["z"].abs() > 2].copy().sort_values("z")
    anom["turnout_pct"] = anom["turnout_pct"].round(1)
    anom["z"] = anom["z"].round(2)
    sheets["5h_precinct_anomalies"] = anom[["locality", "precinct", "voted", "reg", "turnout_pct", "z"]]
    not_rvl = q(hist, f"SELECT SUM(CASE WHEN in_rvl=0 THEN 1 ELSE 0 END) AS not_in_rvl, COUNT(*) total FROM {AB}")
    nrvl = int(not_rvl.not_in_rvl[0])
    md.append("## 5h. Anomaly scan\n")
    md.append(f"Precinct turnout: statewide mean {mean:.1f}%, SD {sd:.1f}pp (precincts with "
              f">=100 active reg; Covington/Sussex excluded). **{len(anom)} precincts** beyond "
              f"±2 SD ({mean-2*sd:.1f}% / {mean+2*sd:.1f}%).\n")
    md.append(df_to_md(anom[["locality", "precinct", "voted", "reg", "turnout_pct", "z"]].head(30)))
    md.append(f"\n**Voters not matching a current RVL record: {nrvl:,} "
              f"({nrvl/int(not_rvl.total[0])*100:.2f}%)** — pre-RVL-refresh new registrations, "
              f"data-quality mismatches, or voters since removed from the roll.\n")

    # ---------- write outputs ----------
    (PROJ / "analysis" / "LTV2026_Ref_Analysis.md").write_text("\n".join(md), encoding="utf-8")
    with pd.ExcelWriter(PROJ / "analysis" / "LTV2026_Ref_Analysis.xlsx", engine="openpyxl") as xw:
        for name, df in sheets.items():
            df.to_excel(xw, sheet_name=name[:31], index=False)

    print("Wrote LTV2026_Ref_Analysis.md and .xlsx")
    print(f"first-time(broad)={ft_broad:,} ({ft_broad/tot*100:.1f}%) | 3-4of4={high:,} vs 0-1of4={low:,}"
          f" | not_in_rvl={nrvl:,} | precinct anomalies={len(anom)}")
    # stash a few headline numbers for the Phase 6 exec summary
    (PROJ / "analysis" / "_headline.json").write_text(json.dumps({
        "base": nbase, "first_time_broad": ft_broad, "first_time_pct": round(ft_broad/tot*100, 1),
        "high_3_4": high, "low_0_1": low, "high_pct": round(high/int(vh.voters.sum())*100, 1),
        "not_in_rvl": nrvl, "precinct_anomalies": len(anom),
        "dem_to": float(dem_to[0]) if len(dem_to) else None,
        "rep_to": float(rep_to[0]) if len(rep_to) else None,
    }), encoding="utf-8")


def df_to_md(df):
    cols = list(df.columns)
    out = ["| " + " | ".join(str(c) for c in cols) + " |",
           "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        vals = []
        for c in cols:
            v = r[c]
            if isinstance(v, float):
                vals.append(f"{v:,.1f}" if v == v else "")
            elif isinstance(v, (int,)):
                vals.append(f"{v:,}")
            else:
                vals.append("" if v is None or (isinstance(v, float) and v != v) else str(v))
        out.append("| " + " | ".join(vals) + " |")
    return "\n".join(out)


if __name__ == "__main__":
    main()
