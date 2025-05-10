# NYC Rent-Stabilized Listings Data Normalization Project

The New York City Rent Guidelines Board [publishes public datasets rent-stabilized apartment listings](https://rentguidelinesboard.cityofnewyork.us/resources/rent-stabilized-building-lists/)
across all five boroughs. All the data lives in PDFs that is hard to work with. This project:
* Cleans up and standardizes NYC.gov's raw listings.
* Makes the data more searchable (via CSV, Google Sheets, visualizations).
* Matches records to StreetEasy for my app [FirstMover](https://www.firstmovernyc.com/), which lets user get StreetEasy
notifications before anyone else.

---

## Codebase Structure

```
├── 1_scanning/
│   ├── scan.py                         # Extracts from PDFs
│   └── Bronx/, Brooklyn/, etc.         # Borough-level outputs
│
├── 2_flatten_and_clean_addresses/
│   └── flatten_and_clean.py           # Flattens 2-address rows
│
├── 3_clean_building_numbers/
│   └── clean_building_numbers.ipynb   # Pattern-specific normalization
│
├── 4_get_coordinates/
│   ├── coordinates.ipynb              # Geocodes addresses using NYC's API
│   └── listings_with_coordinates.csv  # Output with lat/long coordinates
│
├── 5_coordinates_complete/
│   └── listing_with_coordinates_complete.csv  # Final dataset with manually filled missing coordinates
│
├── listings_with_clean_building_no.csv    # Final output
└── README.md
```
---

## Project Workflow

### 1. PDF Parsing (`1_scanning/`)
* Uses `pdfplumber` to extract tabular data from each borough’s PDF.
* Normalizes quirks and layout variations (some had repeated headers, shifted columns, or ghost text).
* Outputs a raw CSV with two sets of address columns (for corner buildings).

### 2. Cleaning the scanned data (`2_flatten_and_clean_addresses/`)

* Flattens `BLDGNO1/STREET1` and `BLDGNO2/STREET2` into one row per address.
* Standardizes:
  * Cardinal directions (e.g. `E` → `East`)
  * Street types (e.g. `Ave` → `Avenue`, `St` → `Street`)
  * Ordinal suffixes (`12Th` → `12th`)

### 3. Building Number Normalization (`3_clean_building_numbers/`)
* Handles the 9 distinct `BUILDING_NO` formats found in NYC datasets.
* Each type (e.g. hyphenated, lettered, fractional) was parsed and expanded where needed.
* Edge cases like `143-19A TO 143-25A` were dissected and exploded into multiple rows with plausible building numbers.

### 4. Geocoding Addresses (`4_get_coordinates/`)
* Uses NYC's Geoclient API to add latitude and longitude coordinates to each address
* Output is stored as `listings_with_coordinates.csv`

### 5. Coordinates Completion (`5_coordinates_complete/`)
* Manual retrieval of coordinates for addresses that couldn't be automatically geocoded in Step 4
* Output is stored as `listing_with_coordinates_complete.csv`

#### Building Number Normalization Deep Dive

StreetEasy and most mapping systems expect a single, clean number (e.g. `2216`, `63-18`, `222R`). NYC’s PDFs are the 
pretty fucked up- especially Queens. Oh, Queens.

This section took the most. It splits, standardizes, or expands each of the following:

| # | Pattern                             | Example(s)                     | Count  |
| - | ----------------------------------- | ------------------------------ |--------|
| 1 | Plain number                        | `2216`                         | 34,884 |
| 2 | Plain range                         | `953 TO 957`                   | 4,768  |
| 3 | Number + letter suffix              | `1684A`, `67R`                 | 234    |
| 4 | Fractional/decimal                  | `151 1/2`, `108.5`             | 32     |
| 5 | Hyphenated (Queens)                 | `63-18`, `19-02`               | 8,188  |
| 6 | Hyphenated range                    | `122-05 TO 122-07`             | 743    |
| 7 | Hyphenated + letter suffix          | `84-24A`                       | 210    |
| 8 | Range with letter suffix            | `711A TO 711D`, `222R TO 224R` | 2      |
| 9 | Hyphenated range with letter suffix | `143-19A TO 143-25A`           | 58     |
|   |                                     |                                | 49,119 |

---

## Challenges & Notes

### PDF variability
* Every borough had different formatting.
* Text alignment issues meant column detection relied on x-coordinates, not headers.

### Address conventions
* Queens-style addresses (`99-16`) required custom logic.
* Ambiguous ranges (`10-26 TO 45595`) were truncated or dropped if invalid.

### Overreporting > Underreporting
* When in doubt, ranges were expanded to err on the side of completeness.

---

## Reproducing This Project

1. **Clone** the repo

```bash
git clone https://github.com/benfwalla/nyc-rent-stabilized-listings.git
```

2. **Install dependencies**

```bash
uv pip install  # or pip install -r requirements.txt
```

3. **Run scripts in order**:

```bash
python 1_scanning/scan.py
python 2_flatten_and_clean_addresses/flatten_and_clean.py
# open and run clean_building_numbers.ipynb sequentially
```
