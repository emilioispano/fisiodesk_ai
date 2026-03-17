import re
from app.text_utils import normalize_text, extract_pain_scores

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

NEGATIVE_LBP_CONTEXT = [
    r"\bcervicalgia\b",
    r"\bdolore cervicale\b",
    r"\bspalla\b",
    r"\bspalla congelata\b",
]

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
]

NON_IMPROVEMENT_PATTERNS = [
    r"\bsituazione stazionaria\b",
    r"\bstazionaria\b",
    r"\blieve peggioramento\b",
    r"\bpeggioramento\b",
    r"\bnessun miglioramento\b",
    r"\bpersistente\b",
]


def score_low_back_pain(text: str) -> float:
    t = normalize_text(text)
    positive_hits = sum(1 for pattern in LBP_PATTERNS if re.search(pattern, t))
    negative_hits = sum(1 for pattern in NEGATIVE_LBP_CONTEXT if re.search(pattern, t))
    score = positive_hits * 1.0 - negative_hits * 0.4
    return max(score, 0.0)


def score_improvement(text: str) -> float:
    t = normalize_text(text)

    positive_hits = sum(1 for pattern in IMPROVEMENT_PATTERNS if re.search(pattern, t))
    negative_hits = sum(1 for pattern in NON_IMPROVEMENT_PATTERNS if re.search(pattern, t))

    score = positive_hits * 1.0 - negative_hits * 1.2

    pain_values = extract_pain_scores(text)
    if len(pain_values) >= 2 and pain_values[0] > pain_values[-1]:
        score += 1.5

    return score
