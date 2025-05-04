from pathlib import Path
import sys
import pdfplumber
import pandas as pd
from collections import defaultdict

# Expected column names in the PDF table
COLS = [
    "ZIP", "BLDGNO1", "STREET1", "STSUFX1",
    "BLDGNO2", "STREET2", "STSUFX2",
    "COUNTY", "CITY",
    "STATUS1", "STATUS2", "STATUS3",
    "BLOCK", "LOT",
]
HDR_SET = set(COLS)

# Remove nearly-duplicate x-coordinates (e.g., when headers repeat slightly offset)
def _dedup(xs, tol=2):
    uniq = []
    for x in sorted(xs):
        if not uniq or abs(x - uniq[-1]) > tol:
            uniq.append(x)
    return uniq

# Detect the horizontal start position of each column
def _get_col_xcoords(page):
    header_xs = [w["x0"] for w in page.extract_words(use_text_flow=False) if w["text"] in HDR_SET]
    return _dedup(header_xs)[:len(COLS)]

# Assign a column index based on horizontal x-position
def _assign_column(x0, col_x0):
    for i, start in enumerate(col_x0):
        if i == len(col_x0) - 1 or x0 < col_x0[i + 1]:
            return i
    return len(col_x0) - 1

# Parse a rent-stabilized housing PDF into a DataFrame
def pdf_to_df(pdf_path: Path) -> pd.DataFrame:
    rows = []

    with pdfplumber.open(pdf_path) as pdf:
        col_x0 = _get_col_xcoords(pdf.pages[0])  # assume first page has headers

        for page in pdf.pages:
            # Extract words loosely grouped by x/y tolerance
            words = page.extract_words(
                x_tolerance=5,
                y_tolerance=2,
                keep_blank_chars=True,
                use_text_flow=False,
            )

            lines = defaultdict(list)
            for w in words:
                txt = w["text"]
                if txt in ("ZIP", "List", "Source:"):  # ignore headers and footers
                    continue
                line_key = round(w["top"])
                col_idx = _assign_column(w["x0"], col_x0)
                lines[line_key].append((col_idx, w["x0"], txt))

            for items in lines.values():
                items.sort(key=lambda t: t[1])  # sort left-to-right
                cols = [""] * len(COLS)
                for col_idx, _, txt in items:
                    cols[col_idx] = f"{cols[col_idx]} {txt}".strip()
                if cols[0][:5].isdigit():  # only include rows starting with a ZIP
                    rows.append(cols)

    df = pd.DataFrame(rows, columns=COLS)

    # Convert numeric columns (ZIP, BLOCK, LOT); leave BLDGNO columns as-is
    df[["ZIP", "BLOCK", "LOT"]] = df[["ZIP", "BLOCK", "LOT"]].apply(
        pd.to_numeric, errors="coerce"
    )

    return df

# Run from command line
if __name__ == "__main__":
    neighborhood = "Staten-Island"
    script_dir = Path(__file__).parent
    neighborhood_path = script_dir / neighborhood
    pdf_file = neighborhood_path / f"{neighborhood}.pdf"

    if not pdf_file.exists():
        print(f"Error: Input PDF not found at {pdf_file}", file=sys.stderr)
        sys.exit(1)

    df = pdf_to_df(pdf_file)
    print(df.head())
    print("Rows parsed:", len(df))

    # Save to CSV in the same folder as the PDF
    neighborhood_path.mkdir(exist_ok=True)
    csv_path = neighborhood_path / f"{neighborhood}.csv"
    df.to_csv(csv_path, index=False)
    print("Saved →", csv_path)
