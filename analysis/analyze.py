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

# Party bucket — matches the absentee/cure dashboard methodology:
# hard party ID first (SD/LD=Dem, SR/LR=Rep), then split ND/U/I by the
# Dem-support score at 50; only no-score / no-VAN-match falls to Unknown.
def party_case(dem_support_expr, likely="LikelyParty"):
    return (f"CASE WHEN {likely} IN ('SD','LD') THEN 'Dem' "
            f"WHEN {likely} IN ('SR','LR') THEN 'Rep' "
            f"WHEN {dem_support_expr} >= 50 THEN 'Dem' "
            f"WHEN {dem_support_expr} < 50 THEN 'Rep' "
            f"ELSE 'Unknown' END")

PARTY_BASE = party_case("dem_support")                                  # base table (dem_support already float)
PARTY_VAN = party_case("TRY_CONVERT(float, Clarity_DemSupport_26)")     # Van view (varchar score)
PARTY_ORDER = ['Dem', 'Rep', 'Unknown']


def eng(db):
    return create_engine(
        f"mssql+pyodbc://INSTANCE-1/{db}"
        "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes",
        fast_executemany=True)


def age_expr(dob_col):
    return (f"DATEDIFF(YEAR, {dob_col}, '{ELECTION_DAY}') - "
            f"CASE WHEN MONTH({dob_col}) > 4 OR (MONTH({dob_col}) = 4 AND DAY({dob_col}) > 21) "
            f"THEN 1 ELSE 0 END")


def base_exists(hist):
    n = pd.read_sql(text(
        "SELECT COUNT(*) n FROM sys.tables WHERE name='LTV2026_Ref_Base'"), hist)["n"][0]
    return int(n) > 0


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
             WHEN TRY_CONVERT(float, v.Clarity_DemSupport_26) >= 50 THEN 'Dem'
             WHEN TRY_CONVERT(float, v.Clarity_DemSupport_26) < 50 THEN 'Rep'
             ELSE 'Unknown' END AS party_bucket,
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


def dropoff_exists(hist):
    n = pd.read_sql(text(
        "SELECT COUNT(*) n FROM sys.tables WHERE name='Dropoff_2025G_Base'"), hist)["n"][0]
    return int(n) > 0


def build_dropoff_base(hist):
    """2025 General voters (still in VAN) + whether they also voted the 2026 referendum."""
    sql = f"""
    IF OBJECT_ID('Historic.dbo.Dropoff_2025G_Base','U') IS NOT NULL
        DROP TABLE Historic.dbo.Dropoff_2025G_Base;
    SELECT
        v.StateFileID,
        v.Age,
        CASE WHEN v.Age BETWEEN 18 AND 24 THEN '18-24' WHEN v.Age BETWEEN 25 AND 34 THEN '25-34'
             WHEN v.Age BETWEEN 35 AND 44 THEN '35-44' WHEN v.Age BETWEEN 45 AND 54 THEN '45-54'
             WHEN v.Age BETWEEN 55 AND 64 THEN '55-64' WHEN v.Age BETWEEN 65 AND 74 THEN '65-74'
             WHEN v.Age >= 75 THEN '75+' ELSE 'Unknown' END AS age_band,
        UPPER(v.Sex) AS sex,
        v.CountyName,
        v.CD,
        v.HD,
        {PARTY_VAN} AS party_bucket,
        CASE WHEN EXISTS (SELECT 1 FROM Historic.dbo.LTV2026_Ref_Votemethod m
                          WHERE m.IDENTIFICATION_NUMBER = v.StateFileID) THEN 1 ELSE 0 END AS voted_ref
    INTO Historic.dbo.Dropoff_2025G_Base
    FROM Voter.dbo.Van v
    WHERE NULLIF(LTRIM(RTRIM(v.General25)),'') IS NOT NULL;
    """
    with hist.begin() as cx:
        cx.execute(text(sql))
        cx.execute(text("CREATE INDEX IX_dropoff_sfid ON Historic.dbo.Dropoff_2025G_Base(StateFileID);"))


def surge_exists(hist):
    n = pd.read_sql(text(
        "SELECT COUNT(*) n FROM sys.tables WHERE name='Surge_2026_Base'"), hist)["n"][0]
    return int(n) > 0


def build_surge_base(hist):
    """Referendum voters (present in VAN) + whether they ALSO voted the 2025 General.
    Surge = voted referendum but NOT 2025G (the flip side of drop-off)."""
    sql = f"""
    IF OBJECT_ID('Historic.dbo.Surge_2026_Base','U') IS NOT NULL
        DROP TABLE Historic.dbo.Surge_2026_Base;
    SELECT
        v.StateFileID,
        v.Age,
        CASE WHEN v.Age BETWEEN 18 AND 24 THEN '18-24' WHEN v.Age BETWEEN 25 AND 34 THEN '25-34'
             WHEN v.Age BETWEEN 35 AND 44 THEN '35-44' WHEN v.Age BETWEEN 45 AND 54 THEN '45-54'
             WHEN v.Age BETWEEN 55 AND 64 THEN '55-64' WHEN v.Age BETWEEN 65 AND 74 THEN '65-74'
             WHEN v.Age >= 75 THEN '75+' ELSE 'Unknown' END AS age_band,
        UPPER(v.Sex) AS sex,
        v.CountyName,
        v.CD,
        v.HD,
        {PARTY_VAN} AS party_bucket,
        CASE WHEN NULLIF(LTRIM(RTRIM(v.General25)),'') IS NOT NULL THEN 1 ELSE 0 END AS voted_2025g
    INTO Historic.dbo.Surge_2026_Base
    FROM Voter.dbo.Van v
    WHERE EXISTS (SELECT 1 FROM Historic.dbo.LTV2026_Ref_Votemethod m
                  WHERE m.IDENTIFICATION_NUMBER = v.StateFileID);
    """
    with hist.begin() as cx:
        cx.execute(text(sql))
        cx.execute(text("CREATE INDEX IX_surge_sfid ON Historic.dbo.Surge_2026_Base(StateFileID);"))


def q(engine, sql):
    return pd.read_sql(text(sql), engine)


def main():
    hist = eng("Historic")
    voter = eng("Voter")

    # Reuse the existing base table unless REBUILD=1 is set (rebuild is the slow part).
    import os
    if base_exists(hist) and os.environ.get("REBUILD") != "1":
        nbase = int(pd.read_sql(text("SELECT COUNT(*) n FROM Historic.dbo.LTV2026_Ref_Base"), hist)["n"][0])
        print(f"Reusing existing LTV2026_Ref_Base ({nbase:,} rows). Set REBUILD=1 to rebuild.")
    else:
        nbase = build_base(hist, voter)

    sheets = {}   # name -> DataFrame for xlsx
    md = []
    md.append("# Referendum 2026 — Voter Pattern Analysis (Phase 5)\n")
    md.append(f"_Generated 2026-05-21. Base table `Historic.dbo.LTV2026_Ref_Base` "
              f"= {nbase:,} LTV voters enriched with Van party/history + RVL match._\n")
    md.append("> **Caveats:** turnout denominators use RVL `STATUS='Active'`; party uses the "
              "absentee-dashboard rule (SD/LD=Dem, SR/LR=Rep, then ND/U/I split by "
              "`Clarity_DemSupport_26` at 50; only no-score/no-VAN = Unknown); baseline = 2025 "
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
        SELECT {PARTY_BASE} AS party_bucket, COUNT(*) AS first_time
        FROM {AB} WHERE (in_van=1 AND prior_vote=0) OR in_van=0
        GROUP BY {PARTY_BASE} ORDER BY first_time DESC""")
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
    vm_party = q(hist, f"SELECT {PARTY_BASE} AS party_bucket, AB_Type, COUNT(*) AS voters FROM {AB} GROUP BY {PARTY_BASE}, AB_Type")
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
    pv = q(hist, f"SELECT {PARTY_BASE} AS party_bucket, COUNT(*) AS voted FROM {AB} GROUP BY {PARTY_BASE}")
    pr = q(voter, f"SELECT {PARTY_VAN} AS party_bucket, COUNT(*) AS registered "
                  f"FROM Voter.dbo.Van GROUP BY {PARTY_VAN}")
    party = pv.merge(pr, on="party_bucket", how="left")
    party["party_bucket"] = pd.Categorical(party["party_bucket"], PARTY_ORDER, ordered=True)
    party = party.sort_values("party_bucket")
    party["turnout_pct"] = (party["voted"] / party["registered"] * 100).round(1)
    party["share_of_voters_pct"] = (party["voted"] / party["voted"].sum() * 100).round(1)
    sheets["5g_party"] = party
    md.append("## 5g. Party (dashboard methodology; denominator = Van registered)\n")
    md.append("Party assigned the same way as the absentee/cure dashboards: hard party ID "
              "(SD/LD=Dem, SR/LR=Rep), then ND/U/I split by `Clarity_DemSupport_26` at 50; "
              "only no-score / no-VAN-match is Unknown. Turnout % = LTV voters / Van registered.\n")
    md.append(df_to_md(party))
    dem_to = party.loc[party.party_bucket == "Dem", "turnout_pct"].values
    rep_to = party.loc[party.party_bucket == "Rep", "turnout_pct"].values
    dem_sh = party.loc[party.party_bucket == "Dem", "share_of_voters_pct"].values
    rep_sh = party.loc[party.party_bucket == "Rep", "share_of_voters_pct"].values
    if len(dem_to) and len(rep_to):
        md.append(f"\nRep turnout {rep_to[0]}% vs Dem turnout {dem_to[0]}% — skew of "
                  f"{abs(dem_to[0]-rep_to[0]):.1f} pp toward {'Rep' if rep_to[0] > dem_to[0] else 'Dem'}. "
                  f"But Democrats were the larger share of the electorate ({dem_sh[0]}% of voters "
                  f"vs {rep_sh[0]}% Republican), consistent with the {'Yes' if dem_sh[0] > rep_sh[0] else 'No'} "
                  f"side winning.\n")

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

    # ---------- 5i Drop-off: 2025 General voters who skipped the referendum ----------
    if not dropoff_exists(hist) or os.environ.get("REBUILD") == "1":
        build_dropoff_base(hist)
    DO = "Historic.dbo.Dropoff_2025G_Base"
    ov = q(hist, f"SELECT COUNT(*) g25, SUM(voted_ref) back, SUM(1-voted_ref) dropped FROM {DO}")
    g25n, back, dropn = int(ov.g25[0]), int(ov.back[0]), int(ov.dropped[0])
    md.append("## 5i. Drop-off — 2025 General voters who skipped the referendum\n")
    md.append(f"Of **{g25n:,}** voters who cast a 2025 General ballot and are still registered in VAN, "
              f"**{back:,} returned ({back/g25n*100:.1f}%)** for the referendum and **{dropn:,} dropped off "
              f"({dropn/g25n*100:.1f}%)**. (An ~80% hold from a Governor's-year general to an April special is "
              f"high.) Drop-off rate below = skipped ÷ 2025G voters in the group.\n")

    dpar = q(hist, f"SELECT party_bucket, COUNT(*) g25_voters, SUM(1-voted_ref) dropped_off FROM {DO} GROUP BY party_bucket")
    dpar["dropoff_pct"] = (dpar.dropped_off / dpar.g25_voters * 100).round(1)
    dpar["party_bucket"] = pd.Categorical(dpar.party_bucket, PARTY_ORDER, ordered=True)
    dpar = dpar.sort_values("party_bucket")
    sheets["5i_dropoff_party"] = dpar
    md.append("By party (dashboard methodology):\n")
    md.append(df_to_md(dpar))

    dage = q(hist, f"SELECT age_band, COUNT(*) g25_voters, SUM(1-voted_ref) dropped_off FROM {DO} GROUP BY age_band")
    dage["dropoff_pct"] = (dage.dropped_off / dage.g25_voters * 100).round(1)
    dage["age_band"] = pd.Categorical(dage.age_band, BAND_ORDER, ordered=True)
    dage = dage.sort_values("age_band")
    sheets["5i_dropoff_age"] = dage
    md.append("\nBy age band:\n")
    md.append(df_to_md(dage))

    dgen = q(hist, f"SELECT sex AS gender, COUNT(*) g25_voters, SUM(1-voted_ref) dropped_off FROM {DO} WHERE sex IN ('M','F') GROUP BY sex")
    dgen["dropoff_pct"] = (dgen.dropped_off / dgen.g25_voters * 100).round(1)
    sheets["5i_dropoff_gender"] = dgen
    md.append("\nBy gender:\n")
    md.append(df_to_md(dgen))

    dcd = q(hist, f"SELECT CD, COUNT(*) g25_voters, SUM(1-voted_ref) dropped_off FROM {DO} WHERE CD IS NOT NULL AND CD<>'' GROUP BY CD ORDER BY CD")
    dcd["dropoff_pct"] = (dcd.dropped_off / dcd.g25_voters * 100).round(1)
    sheets["5i_dropoff_cd"] = dcd
    md.append("\nBy Congressional District:\n")
    md.append(df_to_md(dcd))

    dcc = q(hist, f"SELECT TOP 12 CountyName AS locality, COUNT(*) g25_voters, SUM(1-voted_ref) dropped_off FROM {DO} GROUP BY CountyName ORDER BY SUM(1-voted_ref) DESC")
    dcc["dropoff_pct"] = (dcc.dropped_off / dcc.g25_voters * 100).round(1)
    sheets["5i_dropoff_county_count"] = dcc
    dcr = q(hist, f"SELECT TOP 12 CountyName AS locality, COUNT(*) g25_voters, SUM(1-voted_ref) dropped_off FROM {DO} GROUP BY CountyName HAVING COUNT(*)>=5000 ORDER BY 1.0*SUM(1-voted_ref)/COUNT(*) DESC")
    dcr["dropoff_pct"] = (dcr.dropped_off / dcr.g25_voters * 100).round(1)
    sheets["5i_dropoff_county_rate"] = dcr
    md.append("\nTop 12 localities by drop-off **count** (where the lost voters are):\n")
    md.append(df_to_md(dcc[["locality", "g25_voters", "dropped_off", "dropoff_pct"]]))
    md.append("\nTop 12 localities by drop-off **rate** (min 5,000 2025G voters):\n")
    md.append(df_to_md(dcr[["locality", "g25_voters", "dropped_off", "dropoff_pct"]]))

    BANDS7 = [b for b in BAND_ORDER if b != "Unknown"]
    dap = q(hist, f"SELECT age_band, party_bucket, COUNT(*) g25, SUM(1-voted_ref) dropped FROM {DO} WHERE party_bucket IN ('Dem','Rep') GROUP BY age_band, party_bucket")
    dap["rate"] = (dap.dropped / dap.g25 * 100).round(1)
    sheets["5i_dropoff_age_party"] = dap.sort_values(["age_band", "party_bucket"])
    dpiv = dap.pivot(index="age_band", columns="party_bucket", values="rate").reindex(BANDS7).reset_index()
    dpiv.columns.name = None
    dpiv = dpiv.rename(columns={"Dem": "Dem_dropoff_pct", "Rep": "Rep_dropoff_pct"})
    dpiv["Dem_minus_Rep_pp"] = (dpiv.Dem_dropoff_pct - dpiv.Rep_dropoff_pct).round(1)
    md.append("\nBy age × party — drop-off rate within each age band:\n")
    md.append(df_to_md(dpiv))

    dem_dr = dpar.loc[dpar.party_bucket == "Dem", "dropoff_pct"].values
    rep_dr = dpar.loc[dpar.party_bucket == "Rep", "dropoff_pct"].values
    y_dr = dage.loc[dage.age_band == "18-24", "dropoff_pct"].values
    md.append(f"\n**Takeaway:** drop-off skews young ({y_dr[0] if len(y_dr) else 'n/a'}% of 18–24) and Democratic "
              f"({dem_dr[0] if len(dem_dr) else 'n/a'}% Dem vs {rep_dr[0] if len(rep_dr) else 'n/a'}% Rep) — "
              f"the re-mobilization universe is young, Dem-leaning 2025 voters, concentrated in NoVa/urban "
              f"localities (by count) and college towns (by rate).\n")

    # ---------- 5j Surge: referendum voters who skipped the 2025 General ----------
    if not surge_exists(hist) or os.environ.get("REBUILD") == "1":
        build_surge_base(hist)
    SO = "Historic.dbo.Surge_2026_Base"
    sov = q(hist, f"SELECT COUNT(*) refv, SUM(voted_2025g) returning, SUM(1-voted_2025g) surge FROM {SO}")
    refv, returning, surgen = int(sov.refv[0]), int(sov.returning[0]), int(sov.surge[0])
    md.append("## 5j. Surge — referendum voters who skipped the 2025 General\n")
    md.append(f"Of **{refv:,}** referendum voters present in VAN, **{surgen:,} ({surgen/refv*100:.1f}%)** "
              f"did **not** vote in the 2025 General — the newer / irregular voters this referendum activated "
              f"(vs {returning:,} who voted both). Surge rate below = skipped-2025G ÷ referendum voters in the "
              f"group. (Referendum voters with no VAN record at all — ~25k new registrations — are additional "
              f"surge not counted here.)\n")

    spar = q(hist, f"SELECT party_bucket, COUNT(*) ref_voters, SUM(1-voted_2025g) surge FROM {SO} GROUP BY party_bucket")
    spar["surge_pct"] = (spar.surge / spar.ref_voters * 100).round(1)
    spar["party_bucket"] = pd.Categorical(spar.party_bucket, PARTY_ORDER, ordered=True)
    spar = spar.sort_values("party_bucket")
    sheets["5j_surge_party"] = spar
    md.append("By party (dashboard methodology):\n")
    md.append(df_to_md(spar))

    sage = q(hist, f"SELECT age_band, COUNT(*) ref_voters, SUM(1-voted_2025g) surge FROM {SO} GROUP BY age_band")
    sage["surge_pct"] = (sage.surge / sage.ref_voters * 100).round(1)
    sage["age_band"] = pd.Categorical(sage.age_band, BAND_ORDER, ordered=True)
    sage = sage.sort_values("age_band")
    sheets["5j_surge_age"] = sage
    md.append("\nBy age band:\n")
    md.append(df_to_md(sage))

    sgen = q(hist, f"SELECT sex AS gender, COUNT(*) ref_voters, SUM(1-voted_2025g) surge FROM {SO} WHERE sex IN ('M','F') GROUP BY sex")
    sgen["surge_pct"] = (sgen.surge / sgen.ref_voters * 100).round(1)
    sheets["5j_surge_gender"] = sgen
    md.append("\nBy gender:\n")
    md.append(df_to_md(sgen))

    scd = q(hist, f"SELECT CD, COUNT(*) ref_voters, SUM(1-voted_2025g) surge FROM {SO} WHERE CD IS NOT NULL AND CD<>'' GROUP BY CD ORDER BY CD")
    scd["surge_pct"] = (scd.surge / scd.ref_voters * 100).round(1)
    sheets["5j_surge_cd"] = scd
    md.append("\nBy Congressional District:\n")
    md.append(df_to_md(scd))

    scc = q(hist, f"SELECT TOP 12 CountyName AS locality, COUNT(*) ref_voters, SUM(1-voted_2025g) surge FROM {SO} GROUP BY CountyName ORDER BY SUM(1-voted_2025g) DESC")
    scc["surge_pct"] = (scc.surge / scc.ref_voters * 100).round(1)
    sheets["5j_surge_county_count"] = scc
    md.append("\nTop 12 localities by surge **count**:\n")
    md.append(df_to_md(scc[["locality", "ref_voters", "surge", "surge_pct"]]))

    sap = q(hist, f"SELECT age_band, party_bucket, COUNT(*) refv, SUM(1-voted_2025g) surge FROM {SO} WHERE party_bucket IN ('Dem','Rep') GROUP BY age_band, party_bucket")
    sap["rate"] = (sap.surge / sap.refv * 100).round(1)
    sheets["5j_surge_age_party"] = sap.sort_values(["age_band", "party_bucket"])
    spiv = sap.pivot(index="age_band", columns="party_bucket", values="rate").reindex(BANDS7).reset_index()
    spiv.columns.name = None
    spiv = spiv.rename(columns={"Dem": "Dem_surge_pct", "Rep": "Rep_surge_pct"})
    spiv["Dem_minus_Rep_pp"] = (spiv.Dem_surge_pct - spiv.Rep_surge_pct).round(1)
    md.append("\nBy age × party — surge rate within each age band:\n")
    md.append(df_to_md(spiv))

    s_dem = spar.loc[spar.party_bucket == "Dem", "surge_pct"].values
    s_rep = spar.loc[spar.party_bucket == "Rep", "surge_pct"].values
    s_y = sage.loc[sage.age_band == "18-24", "surge_pct"].values
    md.append(f"\n**Takeaway:** surge (new-to-2025G) voters are disproportionately young "
              f"({s_y[0] if len(s_y) else 'n/a'}% of 18–24 referendum voters skipped 2025G) and lean "
              f"{'Dem' if (len(s_dem) and len(s_rep) and s_dem[0] > s_rep[0]) else 'Rep'} "
              f"({s_dem[0] if len(s_dem) else 'n/a'}% Dem vs {s_rep[0] if len(s_rep) else 'n/a'}% Rep). "
              f"Net churn vs 2025G: ≈{dropn - surgen:+,} ({dropn:,} lost − {surgen:,} gained, VAN-matched).\n")

    # Eligibility caveat: voters who turned 18 between the 2025 General (2025-11-04)
    # and the referendum (2026-04-21) are 'surge' mechanically (couldn't vote 2025G).
    ne = q(hist, """
        SELECT
          SUM(CASE WHEN d.dob > '2007-11-04' AND d.dob <= '2008-04-21' THEN 1 ELSE 0 END) AS newly_elig,
          SUM(CASE WHEN b.age_band='18-24' THEN 1 ELSE 0 END) AS b1824,
          SUM(CASE WHEN b.age_band='18-24' AND b.voted_2025g=0 THEN 1 ELSE 0 END) AS b1824_surge,
          SUM(CASE WHEN b.age_band='18-24' AND d.dob <= '2007-11-04' THEN 1 ELSE 0 END) AS b1824_elig,
          SUM(CASE WHEN b.age_band='18-24' AND d.dob <= '2007-11-04' AND b.voted_2025g=0 THEN 1 ELSE 0 END) AS b1824_elig_surge
        FROM Historic.dbo.Surge_2026_Base b
        JOIN Historic.dbo.LTV2026_Ref l ON l.IDENTIFICATION_NUMBER = b.StateFileID
        CROSS APPLY (SELECT TRY_CONVERT(date, l.DOB, 101) AS dob) d""")
    nelig = int(ne.newly_elig[0])
    raw1824 = int(ne.b1824_surge[0]) / int(ne.b1824[0]) * 100
    elig1824 = int(ne.b1824_elig_surge[0]) / int(ne.b1824_elig[0]) * 100
    md.append(f"\n> _Eligibility note: **{nelig:,}** referendum voters turned 18 after the 2025 General "
              f"(2025-11-04) — eligible for the referendum but not for 2025G — so they count as surge "
              f"mechanically ({nelig/surgen*100:.1f}% of all surge). Excluding them, the 18–24 surge rate is "
              f"**{elig1824:.1f}%** (vs {raw1824:.1f}% reported): the young tilt is overwhelmingly genuine, "
              f"not an artifact of newly-eligible voters._\n")

    # ---------- write outputs ----------
    # Prepend the hand-authored Phase 6 executive summary if present.
    exec_path = PROJ / "analysis" / "_exec_summary.md"
    body = "\n".join(md)
    full = (exec_path.read_text(encoding="utf-8") + "\n" + body) if exec_path.exists() else body
    (PROJ / "analysis" / "LTV2026_Ref_Analysis.md").write_text(full, encoding="utf-8")
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


def _fmt(v):
    import math
    if v is None:
        return ""
    if isinstance(v, str):
        return v
    try:
        f = float(v)
    except (TypeError, ValueError):
        return str(v)
    if math.isnan(f):
        return ""
    if f == int(f):           # whole number -> integer with thousands separators
        return f"{int(f):,}"
    return f"{f:,.1f}"          # otherwise one decimal


def df_to_md(df):
    cols = list(df.columns)
    out = ["| " + " | ".join(str(c) for c in cols) + " |",
           "|" + "|".join(["---"] * len(cols)) + "|"]
    for _, r in df.iterrows():
        out.append("| " + " | ".join(_fmt(r[c]) for c in cols) + " |")
    return "\n".join(out)


if __name__ == "__main__":
    main()
