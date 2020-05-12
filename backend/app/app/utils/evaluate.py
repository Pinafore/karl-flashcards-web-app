from typing import List

from sklearn.metrics.pairwise import cosine_similarity
import logging

from app import models

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
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
    answer_lines = eval_fact.answer_lines
    logger.info("answer_lines: " + str(answer_lines))
    max_score = run_tfidf(typed, answer_lines)
    return evaluate_answer_cutoff(max_score)