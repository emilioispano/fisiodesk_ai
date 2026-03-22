import re
from typing import List

from nltk.stem.snowball import ItalianStemmer
from nltk.tokenize import wordpunct_tokenize

stemmer = ItalianStemmer()


def normalize_text(text):
    # Riporto tutto in minuscolo
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def extract_pain_scores(text):
    # Cerco i pattern del dolore */10 e salvo le progressioni
    t = normalize_text(text)
    matches = re.findall(r"\b([0-9]|10)\s*/\s*10\b", t)
    return [int(x) for x in matches]


def tokenize_text(text):
    # Trasformo la frase in tokens e tengo solo alfanumerici
    t = normalize_text(text)
    tokens = wordpunct_tokenize(t)
    return [tok for tok in tokens if re.search(r"\w", tok)]


def stem_tokens(tokens):
    # PROVA: riduce il dizionario
    return [stemmer.stem(tok) for tok in tokens]


def tokenize_and_stem(text):
    tokens = tokenize_text(text)
    return stem_tokens(tokens)
