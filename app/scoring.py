import re

from app.text_utils import normalize_text, extract_pain_scores, tokenize_and_stem

# Patterns testuali per dolore lombare
LBP_PATTERNS = [
    r"\bdolore lombare\b",
    r"\blombalgia\b",
    r"\bmal di schiena\b",
    r"\brachialgia lombare\b",
    r"\blow back pain\b",
    r"\bdolore alla bassa schiena\b",
    r"\bcolpo della strega\b",
    r"\bzona lombare\b",
    r"\bcolonna lombare\b",
    r"\bmuscolatura lombare\b",
    r"\bbassa schiena\b",
]

# Patterns testuali per problemi lombalgici
NEGATIVE_LBP_CONTEXT = [
    r"\bcervicalgia\b",
    r"\bdolore cervicale\b",
    r"\bspalla\b",
    r"\bspalla congelata\b",
]

# Pattern testuali positivi
IMPROVEMENT_PATTERNS = [
    r"\bmiglioramento\b",
    r"\bmiglioramento significativo\b",
    r"\bnetto miglioramento\b",
    r"\bottimi progressi\b",
    r"\bsta molto meglio\b",
    r"\bbuon recupero\b",
    r"\bcompleta risoluzione\b",
    r"\bnessun dolore residuo\b",
    r"\briduzione significativa\b",
    r"\bmobilità migliorata\b",
    r"\bsituazione eccellente\b",
    r"\bdecisamente diminuito\b",
    r"\bdiminuita sensibilmente\b",
    r"\bcompletamente recuperato\b",
    r"\bquasi completamente risolto\b",
    r"\bcompletamente guarito\b",
]

# Pattern testuali neutri
NON_IMPROVEMENT_PATTERNS = [
    r"\bsituazione stazionaria\b",
    r"\bstazionaria\b",
    r"\bnessun miglioramento\b",
    r"\bpersistente\b",
]

# Pattern testuali negativi
WORSENING_PATTERNS = [
    r"\bpeggioramento\b",
    r"\blieve peggioramento\b",
    r"\bnetto peggioramento\b",
    r"\bprogressivo peggioramento\b",
    r"\briacutizzazione\b",
    r"\bsintomi aumentati\b",
    r"\bdolore aumentato\b",
    r"\bdolore in aumento\b",
    r"\bmaggiore limitazione\b",
    r"\bridotta mobilità\b",
    r"\bpi[uù] dolore\b",
]

# Pattern testuali che puntano al campo semantico della lombalgia
LBP_STEMS = {
    "lomb",
    "schien",
    "rachialg",
}

# Patern testuali che puntano al campo semantico di altri malanni
NEGATIVE_LBP_STEMS = {
    "cervicalg",
    "spall",
}

# Pattern testuali che puntano a un miglioramento
IMPROVEMENT_STEMS = {
    "miglior",
    "progress",
    "recuper",
    "risolu",
    "riduzion",
    "guarit",
    "diminu",
    "mobil",
}

# Pattern testuali che puntano a situazioni neutre
NON_IMPROVEMENT_STEMS = {
    "stazionar",
    "persistent",
}

# Pattern testuali che puntano a peggioramenti
WORSENING_STEMS = {
    "peggior",
    "aument",
    "riacut",
    "limit",
}

# --- DEFINIZIONE DEGLI SCORING ---
# Assegnazione di uno score tanto più alto quanto più probabile è il dolore lombare
def score_low_back_pain(text):
    t = normalize_text(text)
    stems = tokenize_and_stem(text)

    positive_hits = sum(1 for pattern in LBP_PATTERNS if re.search(pattern, t))
    negative_hits = sum(1 for pattern in NEGATIVE_LBP_CONTEXT if re.search(pattern, t))

    stem_positive_hits = sum(1 for s in stems if s in LBP_STEMS)
    stem_negative_hits = sum(1 for s in stems if s in NEGATIVE_LBP_STEMS)

    score = (
        positive_hits * 1.0
        + stem_positive_hits * 0.25
        - negative_hits * 1.0
        - stem_negative_hits * 0.25
    )

    return max(score, 0.0)


# Assegno uno score tanto alto quanto "confident" siamo di un miglioramento
def score_improvement(text):
    t = normalize_text(text)
    stems = tokenize_and_stem(text)

    positive_hits = sum(1 for pattern in IMPROVEMENT_PATTERNS if re.search(pattern, t))
    negative_hits = sum(1 for pattern in NON_IMPROVEMENT_PATTERNS if re.search(pattern, t))
    worsening_hits = sum(1 for pattern in WORSENING_PATTERNS if re.search(pattern, t))

    stem_positive_hits = sum(1 for s in stems if s in IMPROVEMENT_STEMS)
    stem_negative_hits = sum(1 for s in stems if s in NON_IMPROVEMENT_STEMS)
    stem_worsening_hits = sum(1 for s in stems if s in WORSENING_STEMS)

    score = (
        positive_hits * 1.0
        + stem_positive_hits * 0.25
        - negative_hits * 1.0
        - stem_negative_hits * 0.25
        - worsening_hits * 1.25
        - stem_worsening_hits * 0.35
    )

    pain_values = extract_pain_scores(text)
    if len(pain_values) >= 2 and pain_values[0] > pain_values[-1]:
        score += 1.5

    return max(score, 0.0)


# Assegno uno score tanto alto quanto "confident" siamo di un peggioramento
# TODO: ridondante, accorpa con sopra!
def score_worsening(text):
    t = normalize_text(text)
    stems = tokenize_and_stem(text)

    positive_hits = sum(1 for pattern in WORSENING_PATTERNS if re.search(pattern, t))
    soft_hits = sum(1 for pattern in NON_IMPROVEMENT_PATTERNS if re.search(pattern, t))
    improvement_hits = sum(1 for pattern in IMPROVEMENT_PATTERNS if re.search(pattern, t))

    stem_positive_hits = sum(1 for s in stems if s in WORSENING_STEMS)
    stem_soft_hits = sum(1 for s in stems if s in NON_IMPROVEMENT_STEMS)
    stem_improvement_hits = sum(1 for s in stems if s in IMPROVEMENT_STEMS)

    score = (
        positive_hits * 1.5
        + stem_positive_hits * 0.5
        + soft_hits * 0.5
        + stem_soft_hits * 0.25
        - improvement_hits * 1.0
        - stem_improvement_hits * 0.25
    )

    pain_values = extract_pain_scores(text)
    if len(pain_values) >= 2 and pain_values[0] < pain_values[-1]:
        score += 1.5

    return max(score, 0.0)
