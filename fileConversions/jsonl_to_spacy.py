# scripts/to_spacy.py
import sys
import srsly
import spacy
from spacy.tokens import DocBin

"""
Usage:
  python scripts/to_spacy.py assets/train.jsonl assets/train.spacy
  python scripts/to_spacy.py assets/dev.jsonl   assets/dev.spacy
"""

def jsonl_to_spacy(inp_path: str, out_path: str):
    nlp = spacy.blank("en")  # tokenizer only
    db = DocBin(store_user_data=True)

    for eg in srsly.read_jsonl(inp_path):
        text = eg["text"]
        spans = eg.get("spans", [])
        doc = nlp.make_doc(text)
        ents = []
        for sp in spans:
            start, end, label = sp["start"], sp["end"], sp["label"]
            span = doc.char_span(start, end, label=label, alignment_mode="contract")
            if span is None:
                raise ValueError(
                    f"Bad span ({start}, {end}) for text: {text!r}. "
                    "Check offsets/encoding or use alignment_mode='expand' if needed."
                )
            ents.append(span)
        doc.ents = ents
        db.add(doc)

    db.to_disk(out_path)
    print(f"Wrote {out_path}")

if __name__ == "__main__":
    inp, out = sys.argv[1], sys.argv[2]
    jsonl_to_spacy(inp, out)
