# CSV PII Redactor

This project provides a **CSV redaction pipeline** with both **command-line** and **GUI** support to automatically detect and redact sensitive information (PII).  
It uses **regular expressions**, **spaCy**, and **HuggingFace transformers** for Named Entity Recognition (NER), and outputs a sanitized CSV with a summary of detected entities.

---

## Features

- **Regex-based detection** for:
  - Emails  
  - Phone numbers  
  - Credit card numbers  
  - IP addresses

- **NER-based detection**:
  - **spaCy**: PERSON, ORG, GPE, NORP
  - **HuggingFace Transformers**: PER, ORG, LOC

- **Redaction summary**:
  - Total count of redactions  
  - Breakdown by label (e.g., EMAIL, PERSON)  
  - Breakdown by column

- **Flexible replacement tokens**:
  - Use `[REDACTED]` (default) or a custom string  
  - Or leave blank to replace with `[LABEL]` (e.g., `[EMAIL]`)

- **GUI app** (`ui.py`):
  - Browse input/output CSVs  
  - Configure options (sample size, token, disable NER)  
  - View redaction summary with counts by label and column

- **Command-line tool** (`sanitize.py`):
  - End-to-end sanitization pipeline  
  - Toggle NER, spaCy, HuggingFace, or regex-only modes  
  - Intersection mode (only keep overlapping spaCy ∩ HF detections)

---

## Project Structure

```
├── ui.py          # Tkinter GUI for CSV redaction
├── sanitize.py    # CLI entrypoint for redaction pipeline
├── common.py      # Defines Detection dataclass & summary types
├── ingest.py      # CSV loading & heuristic for text columns
├── my_regex.py    # Regex-based detection of PII
├── ner.py         # spaCy & HuggingFace NER wrappers
├── redact.py      # Redaction logic & overlap deduplication
```

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/your-username/pii-redactor.git
cd pii-redactor
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

Dependencies include:
- `pandas`
- `numpy`
- `spacy`
- `transformers`
- `torch`
- `Pillow`
- `tkinter` (bundled with Python on most systems)

*(Make sure to download a spaCy model if needed, e.g. `python -m spacy download en_core_web_sm`)*

---

## Usage

### CLI Mode
```bash
python sanitize.py input.csv output.csv --sample 1000 --token "[MASK]" --no-hf
```

Options:
- `--sample N` → only process first N rows  
- `--no-ner` → disable all NER (regex only)  
- `--no-spacy` → disable spaCy NER  
- `--no-hf` → disable HuggingFace NER  
- `--intersection` → only keep overlapping (spaCy ∩ HF) entities  
- `--token TOKEN` → replacement string (default: `[REDACTED]`)  

### GUI Mode
```bash
python ui.py
```

- Select **input/output CSVs** via file picker  
- Optionally limit sample rows  
- Configure replacement token  
- Toggle **NER on/off**  
- Click **Run Redaction** and view results in the summary box  

---

## Example

**Input CSV**:
```csv
name,email,notes
Alice,alice@example.com,"Call me at 555-123-4567"
```

**Command**:
```bash
python sanitize.py input.csv redacted.csv
```

**Output CSV**:
```csv
name,email,notes
Alice,[EMAIL],"Call me at [PHONE]"
```

**Summary**:
```
TOTAL REDACTION COUNT:
2

REDACTION COUNT BY CATEGORY:
EMAIL: 1
PHONE: 1

REDACTION COUNT BY COLUMN:
email: 1
notes: 1
```

---

## Future Improvements
- Add support for custom regex patterns  
- Configurable entity labels (beyond PERSON/ORG/LOC)  
- Export redaction reports in JSON format  
