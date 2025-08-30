import pandas as pd, ast, srsly, sys

# usage:
# python fileConversions/csv_to_jsonl.py assets/trainingData.csv assets/train.jsonl
# python fileConversions/csv_to_jsonl.py assets/dev.csv assets/dev.jsonl

def convert(csv_path, jsonl_path):
    df = pd.read_csv(csv_path)
    if "text" not in df.columns or "entities" not in df.columns:
        raise ValueError("CSV must have 'text' and 'entities' columns")

    recs = []
    for _, row in df.iterrows():
        text = str(row["text"])
        ents = ast.literal_eval(str(row["entities"]))
        spans = [{"start": int(s), "end": int(e), "label": str(l)} for (s, e, l) in ents]
        recs.append({"text": text, "spans": spans})
    srsly.write_jsonl(jsonl_path, recs)
    print(f"Wrote {len(recs)} records to {jsonl_path}")

if __name__ == "__main__":
    convert(sys.argv[1], sys.argv[2])
