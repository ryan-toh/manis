@echo off
pip install -r requirements.txt
pip install -U spacy transformers
python -m spacy download en_core_web_sm