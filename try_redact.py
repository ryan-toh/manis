import pandas as pd
from common import Detection
from redact import dedupe_overlaps, apply_redactions

# Minimal DF with multiple columns and rows
df = pd.DataFrame({
    "notes": [
        "Call me at 555-123-4567 or email alice@example.com",
        "Server at 192.168.0.1; Bob’s card 4111-1111-1111-1111",
    ],
    "email": ["alice@example.com", "bob@company.org"]
})

# Hand-crafted detections (what regex/NER would normally return)
raw = [
    # row 0, notes
    Detection(row=0, col="notes", start=11, end=23, label="PHONE", value="555-123-4567"),
    Detection(row=0, col="notes", start=33, end=50, label="EMAIL", value="alice@example.com"),
    # row 1, notes
    Detection(row=1, col="notes", start=10, end=21, label="IP", value="192.168.0.1"),
    Detection(row=1, col="notes", start=32, end=51, label="CREDIT_CARD", value="4111-1111-1111-1111"),
    # row 0, email col
    Detection(row=0, col="email", start=0, end=len("alice@example.com"), label="EMAIL", value="alice@example.com"),
]

# Optional: include an intentional overlap to see coalescing
# Example: overlap PHONE by 2 chars (silly but good for testing)
raw.append(Detection(row=0, col="notes", start=9, end=23, label="PHONE", value="at 555-123-4567"))

# 1) Clean overlaps
clean = dedupe_overlaps(raw)

# 2) Apply redactions
redacted_df, summary = apply_redactions(df, clean, token="[REDACTED]")

print("=== Redacted DF ===")
print(redacted_df)
print("\n=== Summary ===")
print(summary)
