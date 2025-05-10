import pandas as pd
import re
from pathlib import Path

# File paths
INPUT_CSV = Path("../1_scanning/All NYC scanned.csv")
OUTPUT_CSV = Path("listings_flattened_and_cleaned_address.csv")

# Common abbreviations for directionals and street types
DIRECTIONALS = {
    "N": "North", "NE": "Northeast", "E": "East", "SE": "Southeast",
    "S": "South", "SW": "Southwest", "W": "West", "NW": "Northwest",
}

STREET_TYPES = {
    "ST": "Street", "AVE": "Avenue", "RD": "Road", "BLVD": "Boulevard",
    "DR": "Drive", "PKWY": "Parkway", "PL": "Place", "CIR": "Circle",
    "CT": "Court", "TER": "Terrace", "LN": "Lane", "SQ": "Square",
    "MALL": "Mall", "CRES": "Crescent", "EXT": "Extension", "OVAL": "Oval",
    "WALK": "Walk", "WAY": "Way", "PATH": "Path", "RTE": "Route",
    "HTS": "Heights", "GDN": "Garden", "GDNS": "Gardens", "PLZ": "Plaza",
    "HWY": "Highway", "BCH": "Beach", "VLG": "Village", "ROW": "Row",
    "MNR": "Manor", "EST": "Estate", "ESTS": "Estates", "EXPY": "Expressway"
}

def clean_street_name(street_raw, suffix_raw=None):
    """
    Takes raw street and suffix values, expands abbreviations, fixes capitalization and ordinals.
    Example: '123 ST' + 'E' → '123 East Street'
    """
    if pd.isna(street_raw):
        return None

    street = str(street_raw).strip().upper()
    suffix = str(suffix_raw).strip().upper() if pd.notna(suffix_raw) else ""

    if suffix:
        street = f"{street} {suffix}"

    tokens = street.split()
    expanded = []

    for token in tokens:
        if token in DIRECTIONALS:
            expanded.append(DIRECTIONALS[token])
        elif token in STREET_TYPES:
            expanded.append(STREET_TYPES[token])
        else:
            expanded.append(token)

    # Title-case and fix ordinals like 12Th → 12th
    s = " ".join(expanded).title()
    s = re.sub(r'(\d+)(St|Nd|Rd|Th)\b', lambda m: f"{m.group(1)}{m.group(2).lower()}", s, flags=re.IGNORECASE)
    return re.sub(r'\s+', ' ', s).strip()

def flatten_rent_stabilized(input_csv: Path, output_csv: Path):
    """
    Reads a rent-stabilized apartment CSV, flattens two address columns into one list,
    standardizes street names, converts decimals numbers to fractions, and writes the cleaned result to a new CSV.
    """
    df = pd.read_csv(input_csv, dtype=str)
    rows = []

    for _, row in df.iterrows():
        for bldg_col, street_col, suffix_col in [("BLDGNO1", "STREET1", "STSUFX1"), ("BLDGNO2", "STREET2", "STSUFX2")]:
            bldgno = row.get(bldg_col)
            street = row.get(street_col)
            suffix = row.get(suffix_col)

            if pd.notna(bldgno) and pd.notna(street):
                # Handle .5 addresses as fractions
                clean_bldgno = str(bldgno)
                if re.match(r'^\d+\.5$', clean_bldgno):
                    clean_bldgno = re.sub(r'\.5$', ' 1/2', clean_bldgno)
                    print(f"Converted {bldgno} to {clean_bldgno}")

                cleaned_street = clean_street_name(street, suffix)
                rows.append({
                    "BOROUGH": row.get("BOROUGH"),
                    "ZIP": str(row.get("ZIP")).zfill(5) if pd.notna(row.get("ZIP")) else None,
                    "BUILDING_NO": clean_bldgno,
                    "STREET": cleaned_street,
                    "BLOCK": row.get("BLOCK"),
                    "LOT": row.get("LOT"),
                    "COUNTY": row.get("COUNTY"),
                    "CITY": row.get("CITY"),
                    "STATUS1": row.get("STATUS1"),
                    "STATUS2": row.get("STATUS2"),
                    "STATUS3": row.get("STATUS3"),
                })

    pd.DataFrame(rows).to_csv(output_csv, index=False)
    print(f"Wrote {len(rows)} rows to {output_csv}")

if __name__ == "__main__":
    flatten_rent_stabilized(INPUT_CSV, OUTPUT_CSV)
