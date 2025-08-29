import pandas as pd
from common import Detection
from redact import dedupe_overlaps, apply_redactions

df = pd.DataFrame({
    "notes": [
        "Call me at 555-123-4567 or email alice@example.com",
        "Server at 192.168.0.1; Bob’s card 4111-1111-1111-1111",
    ],
    "email": ["alice@example.com", "bob@company.org"]
})

raw = [
    # row 0, notes
    Detection(row=0, col="notes", start=11, end=23, label="PHONE", value="555-123-4567"),
    Detection(row=0, col="notes", start=33, end=50, label="EMAIL", value="alice@example.com"),
    # row 1, notes
    Detection(row=1, col="notes", start=10, end=21, label="IP", value="192.168.0.1"),
    Detection(row=1, col="notes", start=34, end=53, label="CREDIT_CARD", value="4111-1111-1111-1111"),
    # row 0, email col
    Detection(row=0, col="email", start=0, end=len("alice@example.com"), label="EMAIL", value="alice@example.com"),
]

raw.append(Detection(row=0, col="notes", start=9, end=23, label="PHONE", value="at 555-123-4567"))

clean = dedupe_overlaps(raw)

redacted_df, summary = apply_redactions(df, clean, token="[REDACTED]")

print("=== Redacted DF ===")
print(redacted_df)
print("\n=== Summary ===")
print(summary)
