from typing import List

from app import models
from sklearn.metrics.pairwise import cosine_similarity

from app.utils.utils import logger, log_time, time_it
import os
import pickle

corpus: List[str] = []
dirname = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(dirname, '../data/tfidf.pkl')
with open(filename, "rb") as pickleFile:
    tfidf = pickle.load(pickleFile)


def run_tfidf(true_answer: str, texts_to_score: List[str]) -> int:
    text_vec = tfidf.transform(texts_to_score)
    ans_vec = tfidf.transform([true_answer])
    scores = cosine_similarity(ans_vec, text_vec)[0].tolist()
    logger.info("scores: " + str(scores))
    return max(scores)


def evaluate_answer_cutoff(max_score: float) -> bool:
    if max_score > .15:
        return True
    else:
        return False


def evaluate_answer(eval_fact: models.Fact, typed: str) -> bool:
    cleaned_back = eval_fact.answer.lower().strip()
    cleaned_typed = typed.lower().strip()
    answer_lines = [answer_line.lower() for answer_line in eval_fact.answer_lines] + [cleaned_back]
    max_score = run_tfidf(cleaned_typed, answer_lines)
    return evaluate_answer_cutoff(max_score)
