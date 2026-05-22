"""
export_dropoff_targets.py
-------------------------
Exports the 2025-General -> 2026-referendum DROP-OFF voters (people who voted in
the 2025 General but skipped the April 2026 referendum) as VAN-ready CSVs for
re-mobilization outreach.

*** PRIVACY ***
Output contains individual voter PII (name, address, phone). It is written to a
folder OUTSIDE the git repo (OUT_DIR below) and must NEVER be committed to the
public referendum-2026 repository. This script (code only, no PII) is safe to commit.

Source: Historic.dbo.Dropoff_2025G_Base (built by analyze.py) joined to Voter.dbo.Van.
"""

from datetime import date
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text

# External, NON-repo location for the PII output:
OUT_DIR = Path(r"C:\Absentee\Referendum2026_Dropoff_Targets")


def eng():
    return create_engine(
        "mssql+pyodbc://INSTANCE-1/Historic"
        "?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes")


BASE_SQL = """
SELECT
    v.VoterFileVANID, d.StateFileID,
    v.LastName, v.FirstName, v.MiddleName,
    v.PreferredPhone, v.CellPhone,
    v.Address, v.City, v.Zip5,
    d.CountyName, d.CD, d.HD,
    d.party_bucket, d.Age, d.sex
FROM Historic.dbo.Dropoff_2025G_Base d
JOIN Voter.dbo.Van v ON v.StateFileID = d.StateFileID
WHERE d.voted_ref = 0
"""


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    e = eng()
    today = date.today().isoformat()

    full = pd.read_sql(text(BASE_SQL), e)
    full = full.sort_values(["CD", "CountyName", "LastName", "FirstName"])
    f_all = OUT_DIR / f"dropoff_all_{today}.csv"
    full.to_csv(f_all, index=False)

    # Recommended priority segment: Dem-leaning, under 50
    seg = full[(full.party_bucket == "Dem") & (full.Age.notna()) & (full.Age < 50)]
    f_seg = OUT_DIR / f"dropoff_Dem_under50_{today}.csv"
    seg.to_csv(f_seg, index=False)

    print(f"Wrote (PII, external — NOT in repo):")
    print(f"  {f_all}  ({len(full):,} drop-off voters)")
    print(f"  {f_seg}  ({len(seg):,} Dem-leaning under-50)")


if __name__ == "__main__":
    main()
