# NYC Rent-Stabilized Listings Data Normalization Project

## Overview
This project extracts, cleans, and standardizes data on rent-stabilized apartment buildings in New York City, producing 
a clean CSV suitable for analysis.The raw data is sourced from the Rent Stabilized Buildings Lists published by the 
NYC.gov Rent Guidelines Board. The process addresses the significant inconsistencies and formatting challenges inherent 
in the original datasets.

## Data Source
[Rent Stabilized Buildings Lists](https://www.nycrgb.org/html/resources/rentstab.html)
The site provides PDFs for each borough, listing rent-stabilized buildings as of October 2024.

## Project Workflow

### PDF Collection & Parsing

* Download and extract data from borough-specific PDFs.
* Each PDF has its own quirks in formatting and structure.

### Address Flattening & Cleaning

* Standardize street names.
* Handle multi-address listings.
* Convert raw data into a consistent tabular format.

### Building Number Normalization

* Apply borough-specific rules to standardize building numbers.
* Account for NYC’s unique address conventions.

### CSV Output

* Export the cleaned, analysis-ready dataset for further use.

## Codebase Structure

```
├── 1_scanning/
│   ├── scan.py                         # Downloads and parses borough PDFs
│   ├── Bronx/, Brooklyn/, ...         # Intermediate files per borough
│   └── All NYC scanned.csv            # Aggregated raw data
│
├── 2_flatten_and_clean_addresses/
│   ├── flatten_and_clean.py           # Flattens and standardizes addresses
│   └── listings_flattened_and_cleaned_address.csv
│
├── 3_clean_building_numbers/
│   ├── clean_building_numbers.ipynb   # Cleans and normalizes building numbers
│   └── listings_with_clean_building_no.csv
│
├── README.md
└── pyproject.toml, uv.lock            # Dependencies
```

## Data Cleaning Details

### Cleaning `STREET`

> *(This section can be expanded with more detail if needed.)*

### Cleaning `BUILDING_NO`

The `BUILDING_NO` column represents the building’s street number.
Due to the diversity of NYC address conventions and inconsistent data entry, cleaning this field required handling a variety of patterns:

* **Plain numbers:** `2216`, common in Manhattan, Bronx, Brooklyn.
* **Ranges:** `953 TO 957`, for connected buildings.
* **Hyphenated numbers:** `63-18`, common in Queens.
* **Letter suffixes:** `1684A`, `67R`, for subunits.
* **Fractions/Decimals:** `151 1/2`, `48.5`, for small or split properties.

In the dataset of 49,119 records, each `BUILDING_NO` fell into one of nine patterns:

| # | Pattern                             | Example(s)                               | Count      |
| - | ----------------------------------- | ---------------------------------------- | ---------- |
| 1 | Plain number (just digits)          | `2216`, `2220`, `2224`                   | 34,884     |
| 2 | Plain range (X TO Y)                | `953 TO 957`, `791 TO 799`               | 4,768      |
| 3 | Number + letter suffix              | `1684A`, `1684B`, `1684C`                | 234        |
| 4 | Fractional or decimal number        | `151 1/2`, `108.5`, `129 1/2`            | 32         |
| 5 | Hyphenated number (Queens style)    | `2-6`, `19-02`, `63-18`                  | 8,188      |
| 6 | Hyphenated range (X-XX TO Y-YY)     | `122-05 TO 122-07`, `123-99 TO 124-01`   | 743        |
| 7 | Hyphenated + letter suffix          | `34-72A`, `84-24A`, `172-25A`            | 210        |
| 8 | Range with letter suffix            | `222R TO 224R`, `711A TO 711D`           | 2          |
| 9 | Hyphenated range with letter suffix | `143-19A TO 143-25A`, `64-46A TO 64-72B` | 58         |
|   | **Total**                           |                                          | **49,119** |

### Special Challenges: Queens

Queens addresses required custom logic due to the prevalence of block-building hyphenation and ambiguous ranges:

* `10-26 TO 45595`: Treated as an error; only the first number was used.
* `73-01 TO 75-99`: Spans multiple blocks and hundreds of buildings. Cleaning split the range by block and generated plausible building numbers.

## Lessons & Challenges

* **PDF Parsing:** Each borough’s PDF had inconsistent formatting, requiring custom extraction logic.
* **Address Diversity:** NYC’s address conventions (especially in Queens) necessitated borough-specific cleaning strategies.
* **Ambiguity Handling:** When unclear, the process favored overreporting to preserve data integrity.

## How to Reproduce

1. Clone the repository.
2. Install dependencies:

```bash
pip install -r requirements.txt
# or if using Poetry or uv
uv pip install
```

3. Run the scripts in order:

   * `1_scanning/scan.py`
   * `2_flatten_and_clean_addresses/flatten_and_clean.py`
   * `3_clean_building_numbers/clean_building_numbers.ipynb`

Each stage produces an intermediate cleaned CSV.

## Output

**Final cleaned CSV:**
`3_clean_building_numbers/listings_with_clean_building_no.csv`
This file contains the standardized, analysis-ready dataset.

## Next Steps

* Update borough-specific logic as new quirks are discovered.
* Automate PDF downloads for future data releases.
* Consider building a dashboard or API for easier access.

---

Let me know if you'd like a `README.md` file exported.
